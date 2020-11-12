from django.http import HttpResponse
from django.shortcuts import render

# Create your viewsets here.

def protectedMedia(request, org_id, doc_id, folder, doc):
    if 1 == 1:
        print("good good good good good good good good good good good good good good good good")
        print(request)
        response = HttpResponse()
        #response["Content-Disposition"] = "attachment"
        response['X-Accel-Redirect'] = '/protectedMedia/uploads/document/' + org_id + '/' + doc_id + '/' + folder + '/' + doc
        print(response['X-Accel-Redirect'])
        return response
    else:
        return HttpResponse(status=400)