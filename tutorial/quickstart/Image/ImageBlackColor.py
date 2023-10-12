import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import numpy as np  
from io import BytesIO
from PIL import Image
import base64

import fastai
from deoldify import device
from deoldify.visualize import *
import warnings

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .* set is empty.*?")

# Initialize DeOldify colorizer
colorizer = get_image_colorizer(artistic=True)

class ImageBlackColor(APIView):
    def post(self, request, format=None):
        try:
            received_data = request.FILES.get('image')
            
            if received_data:
                original_filename = received_data.name
                img = Image.open(received_data)
                
                
                # Check if the image is not in grayscale
                if img.mode != 'L':
                    # Convert the image to grayscale
                    img = img.convert('L')
                       
                input_array = np.array(img)
                image_buffer = io.BytesIO()
                image = Image.fromarray(input_array)
                image.save(image_buffer, format='PNG')
                image_buffer.seek(0)
                # Colorize the image using DeOldify
                colorized_image = colorizer.get_transformed_image(image_buffer)

                filename_without_extension, file_extension = os.path.splitext(original_filename)

               

                # Convert the image to base64
                response_data = {
                    'image_name': filename_without_extension + "_colorized.png",
                    'image_base64': image_to_base64(colorized_image, "png"),
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
