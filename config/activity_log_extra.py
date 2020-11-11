import json
def make_extra_data(request, response, body):

    return json.dumps({'request':str(request.META),'body':str(body)})