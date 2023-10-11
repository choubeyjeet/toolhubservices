from django.shortcuts import render
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, PageBreak, Image as RLImage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from io import BytesIO
from PIL import Image
import os
import uuid

class ImageToPdf(APIView):

    def post(self, request, format=None):
        try:
            received_data = request.FILES.getlist('images')
            pageType = request.POST.get('pageType', 'portrait')

            pdf_folder = 'files'  # Folder name where PDFs will be stored
            os.makedirs(pdf_folder, exist_ok=True)

            # Generate a unique filename for the PDF using UUID
            unique_filename = str(uuid.uuid4()) + '.pdf'
            pdf_filename = os.path.join(pdf_folder, unique_filename)

            # Create a PDF document with the selected page orientation
            if pageType == 'Landscape':
                doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter))
            else:
                doc = SimpleDocTemplate(pdf_filename, pagesize=portrait(letter))

            elements = []
            for image_file in received_data:
                image = Image.open(image_file)

                # Calculate the maximum width and height based on the page size
                max_width = doc.width
                max_height = doc.height

                # Check if the image dimensions exceed the maximum width or height
                if image.width > max_width or image.height > max_height:
                    # Resize the image while maintaining the aspect ratio
                    image.thumbnail((max_width, max_height))

                rl_image = RLImage(image_file, width=image.width, height=image.height)
                elements.append(rl_image)
                elements.append(PageBreak())

            doc.build(elements)

            return Response({"status": "ok", "pdf_filename": unique_filename})

        except Exception as e:
            print(str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
