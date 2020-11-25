from django.shortcuts import render
from apps.l_core.doc_tools import get_help_text_from_apps

def db_structure_view(request):
    #http://10.0.44.244:8000/api/api-doc/?apps=document,contracts
    apps = request.GET['apps'].split(',')
    apps_data = get_help_text_from_apps(apps_to_doc=apps)
    return render(request, 'doc_tools/model_structure.html', {"apps": apps_data})