from django.shortcuts import render
from .models import ClientFormSettings

def component_permission_view(request):
    data = ClientFormSettings.objects.all()
    return render(request, 'component_permission_structure.html', {"data": data})