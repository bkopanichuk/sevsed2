from django.http import HttpResponse
from django.shortcuts import render
from apps.document.models.document_model import BaseDocument
from apps.document.api.srializers.document_serializer import DocumentSerializer


# Create your viewsets here.

def protectedMedia(request, org_id, doc_id, folder, doc):
    if 1 == 1:
        print("good good good good good good good good good good good good good good good good")
        print(request)
        response = HttpResponse()
        # response["Content-Disposition"] = "attachment"
        response[
            'X-Accel-Redirect'] = '/protectedMedia/uploads/document/' + org_id + '/' + doc_id + '/' + folder + '/' + doc
        print(response['X-Accel-Redirect'])
        return response
    else:
        return HttpResponse(status=400)


def public_document_details(request, doc_uuid):
    doc = BaseDocument.objects.get(unique_uuid=doc_uuid)
    doc_serializer = DocumentSerializer(instance=doc,context={"request":request})
    return render(request, 'details/document_details.html', {"doc_data": doc_serializer.data})
