import json
from django.utils.deprecation import MiddlewareMixin
from pycallgraph import Config
from pycallgraph import PyCallGraph
from pycallgraph.globbing_filter import GlobbingFilter
from pycallgraph.output import GraphvizOutput, GephiOutput
import time
from django.conf import settings


class DeserializeJson(MiddlewareMixin):
    def process_request(self, request):
        ##l =dir(request.POST)
        in_data = request.POST
        request.POST._mutable = True
        for key in request.POST.keys():
            value = request.POST.get(key)
            if type(value) == str:
                try:
                    value_json = json.loads(value)
                    setattr(request, key, value_json)
                except Exception as e:
                    pass
        out_data = request.POST
        ##aise Exception 


class PyCallGraphMiddleware(MiddlewareMixin):
    VALID_OUTPUT_TYPE = ['png', 'dot','pdf','json']
    DEFAULT_EXCLUDE = ['*.__unicode__', '*.__str__']

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and 'graph' in request.GET:
            visualize_modules = request.GET['graph'].split(',')
            exclude_extra = request.GET.get('exclude_extra','').split(',')
            exclude = PyCallGraphMiddleware.DEFAULT_EXCLUDE + exclude_extra
            graph_output = request.GET.get('graph_output', 'png')
            groups = request.GET.get('groups', False)
            max_depth = int(request.GET.get('max_depth', 99999))
            tool = request.GET.get('tool', 'dot')
            ##https://graphviz.org/
            ## Roadmap

            if graph_output not in PyCallGraphMiddleware.VALID_OUTPUT_TYPE:
                raise Exception(f'"{graph_output}" not in "{PyCallGraphMiddleware.VALID_OUTPUT_TYPE}"')

            output_file = 'pycallgraph-{}-{}.{}'.format(time.time(), tool, graph_output)


            output = GraphvizOutput(output_file=output_file, tool=tool,output_type=graph_output)


            config = Config(groups=groups,max_depth=max_depth)
            config.trace_filter = GlobbingFilter(include=visualize_modules, exclude=exclude)

            pycallgraph = PyCallGraph(output=output, config=config)
            pycallgraph.start()

            self.pycallgraph = pycallgraph


    def process_response(self, request, response):
        if settings.DEBUG and 'graph' in request.GET and hasattr(self, 'pycallgraph'):
            self.pycallgraph.done()

        return response
