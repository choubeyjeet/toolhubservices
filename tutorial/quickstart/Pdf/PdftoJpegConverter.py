import os
import tempfile
from django.http import Http404, FileResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import fitz  # PyMuPDF
import zipfile
import io
import uuid

class PdftoJpegConverter(APIView):

    def post(self, request, format=None):

        received_data = request.FILES.get('pdf')
        file_type = request.POST.get('type')

        if not received_data:
            return Response({"error": "No pdf file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save the uploaded PDF to a temporary file
            temp_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_pdf_file.write(received_data.read())
            temp_pdf_file.close()

            if file_type == "zip":
                # Create a unique filename for the ZIP file
                converted_filename = f"{uuid.uuid4().hex}.zip"

                # Define the output ZIP file path
                output_path = os.path.join("files", converted_filename)

                # Create a temporary directory to store images
                temp_image_dir = tempfile.mkdtemp(prefix='temp_images_')
                
                # Initialize a ZIP file to store images
                with zipfile.ZipFile(output_path, 'w') as zipf:
                    # Open the PDF file
                    pdf_document = fitz.open(temp_pdf_file.name)
                    
                    # Iterate through pages
                    for page_num in range(len(pdf_document)):
                        
                        page = pdf_document.load_page(page_num)

                        # Render the page as an image (adjust DPI as needed)
                        image = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
                        
                        # Save the image as a JPEG file
                        img_path = os.path.join(temp_image_dir, f'page_{page_num + 1}.jpeg')
                        image.save(img_path, 'jpeg')

                        # Add the image file to the ZIP archive
                        zipf.write(img_path, os.path.basename(img_path))

                # Clean up: Remove the temporary image directory
                for file in os.listdir(temp_image_dir):
                    os.remove(os.path.join(temp_image_dir, file))
                os.rmdir(temp_image_dir)

                return JsonResponse({"path": converted_filename})

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
