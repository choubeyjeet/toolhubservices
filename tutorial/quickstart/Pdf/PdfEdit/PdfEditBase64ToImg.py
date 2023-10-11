import os
import tempfile
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import fitz  # PyMuPDF
import base64
import uuid

class PdfEditBase64ToImg(APIView):

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

            if file_type == "jpeg":
                # Create a temporary directory to store JPEG images
                temp_image_dir = tempfile.mkdtemp(prefix='temp_images_')

                # Open the PDF file
                pdf_document = fitz.open(temp_pdf_file.name)

                image_data_list = []

                # Iterate through pages
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)

                    # Render the page as an image (adjust DPI as needed)
                    image = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))

                    # Save the image as a JPEG file
                    img_path = os.path.join(temp_image_dir, f'page_{page_num + 1}.jpeg')
                    image.save(img_path, 'jpeg')

                    # Read the JPEG image as bytes and encode it to base64
                    with open(img_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        img_data_with_prefix = f"data:image/jpeg;base64,{img_data}"
                    # Add image data along with page sequence
                    image_data_list.append({
                        'page': page_num + 1,
                        'imageData': img_data_with_prefix,
                    })

                # Clean up: Remove the temporary image directory
                for file in os.listdir(temp_image_dir):
                    os.remove(os.path.join(temp_image_dir, file))
                os.rmdir(temp_image_dir)

                return JsonResponse({"pages": image_data_list})
              
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
