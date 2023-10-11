from django.shortcuts import render
import rembg
import numpy as np
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from io import BytesIO
from PIL import Image, ImageFilter
import base64
import requests
import re
import cv2
class ImageRemoveBackground(APIView):

    def post(self, request, format=None):
        try:
            received_color = request.POST.get('color')
            received_data = request.FILES.get('images')
            bg_Image = request.FILES.get('bgImg');
            bg_Type = request.POST.get('type')
            pattern = r'https:\/\/|http:\/\/|www\.'
            validUrl = re.search(pattern, received_color)
            

            if received_data:
                original_filename = received_data.name
                type = original_filename.split('.')[-1]
                img = Image.open(received_data)

                input_array = np.array(img)
                
                if not validUrl and bg_Type != 'removeBg':
                    
                    if received_color != 'undefined':
                        
                        # Use the provided color as the background
                        r, g, b = parse_color(received_color)
                        background_color = (r, g, b)
                        output_array = rembg.remove(input_array, bg_color=background_color)
                        output_image = Image.fromarray(output_array)
                        img_base64 = image_to_base64(output_image, type, background_color)
                    else:
                        # Use transparent background if color is missing
                        background_color = None
                        output_array = rembg.remove(input_array, bg_color=background_color)
                        output_image = Image.fromarray(output_array)
                        img_base64 = image_to_base64(output_image, type, background_color)
                else:
                        
                    
                    if bg_Type == "removeBg":
                        
                        background_img = Image.open(bg_Image)
                        
                        
                        
                        #background_img = Image.open(BytesIO(requests.get(received_color).content));
                        output_array_b = rembg.remove(input_array, bg_color=None)
                        output_imageB = Image.fromarray(output_array_b)
                        background_img = background_img.resize((output_imageB.size))
                        
                        output_image = Image.new('RGBA', output_imageB.size)
                        
                        
                    else:
                        
                        background_img = Image.open(BytesIO(requests.get(received_color).content));
                        output_array_b = rembg.remove(input_array, bg_color=None)
                        output_imageB = Image.fromarray(output_array_b)
                        background_img = background_img.resize((output_imageB.size))
                        output_image = Image.new('RGBA', output_imageB.size)    
                        
                    
                    #output_imageB = output_imageB.filter(ImageFilter.MedianFilter(size=9))
                    output_image.paste(background_img, (0, 0))
                    output_image.paste(output_imageB, (0, 0), output_imageB)
                    img_base64 = image_to_base64(output_image, type, None)
                    
                    
                filename_without_extension = original_filename.rsplit('.', 1)[0]

                response_data = {
                    'image_name': filename_without_extension + ".png",
                    'image_base64': img_base64,
                }

                return Response(response_data)
            else:
                raise Http404
        except Exception as e:
            print(str(e))
            Response("Balle Balle")


def image_to_base64(image, type, background_color):
    buffered = BytesIO()

    # Get the image format (e.g., JPEG, PNG)
    if type == 'jpg':
        type = 'jpeg'

    if background_color is None:
        # If background_color is None, use transparent background
        img = image.convert('RGBA')
    else:
        # Create a new image with the specified background color
        img = Image.new('RGBA', image.size, background_color)
        img.paste(image, (0, 0), image)

    # Convert the image to a BytesIO object in PNG format
    img.save(buffered, format="PNG")

    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Determine the appropriate image MIME type
    mime_type = f'image/png'

    # Combine the data prefix and Base64-encoded string
    data_uri = f'data:{mime_type};base64,{img_base64}'

    return data_uri


def parse_color(color_str):
    # Parse the color string in the format "RGB(0, 0, 255)"
    color_values = color_str.strip("RGB()").split(",")
    r, g, b = map(int, color_values)
    return r, g, b