import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import numpy as np
from io import BytesIO
import base64
import cv2

class ImageRestore(APIView):
    def post(self, request, format=None):
        try:
            received_data = request.FILES.get('image')

            if received_data:
                original_filename = received_data.name
                img = Image.open(received_data)

                # Convert the image to grayscale
                img = img.convert('L')

                # Convert to NumPy array
                input_array = np.array(img)

                # Denoise using bilateral filter
                denoised_image = cv2.bilateralFilter(input_array, d=9, sigmaColor=75, sigmaSpace=75)

                # Convert the restored image to PIL format
                restored_pil_image = Image.fromarray(denoised_image)

                # Convert the restored image to base64
                response_data = {
                    'image_name': original_filename,
                    'image_base64': image_to_base64(restored_pil_image, "png"),
                }

                return Response(response_data)
            else:
                raise Http404
        except Exception as e:
            return Response("Error occurred")

def image_to_base64(image, type):
    buffered = BytesIO()
    img = image
    img.save(buffered, format=type)

    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    mime_type = f'image/{type}'

    data_uri = f'data:{mime_type};base64,{img_base64}'

    return data_uri
