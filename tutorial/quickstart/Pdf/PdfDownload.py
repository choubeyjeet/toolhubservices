
import os
from django.http import HttpResponse
from django.views.generic import View

class DownloadPDF(View):

    def get(self, request, *args, **kwargs):
        file_name = request.GET.get('file')

        if not file_name:
            return HttpResponse("Invalid request. Missing 'file' parameter.", status=400)

        try:
            # Define the path to the converted DOCX file (adjust as needed)
            docx_file_path = os.path.join("files", file_name)

            # Set the Content-Disposition header to trigger download
            response = HttpResponse(content_type='application/docx')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'

            # Serve the file content
            with open(docx_file_path, 'rb') as docx_file:
                response.write(docx_file.read())
            os.remove(docx_file_path)
            return response

        except Exception as e:
            print(e)
            return HttpResponse("Error while serving the file.", status=500)
