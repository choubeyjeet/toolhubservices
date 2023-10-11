from django.shortcuts import render
import rembg
import numpy as np
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from io import BytesIO
from PIL import Image
import base64
import cv2
class ImageToSketch(APIView):

    def post(self, request, format=None):

        recevied_data = request.FILES.get('images')
        sketch_type = request.POST.get('type')
        if not recevied_data:
            return Response({"error": "No image file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            original_filename = recevied_data.name
            type = original_filename.split('.')[-1]
            
            img = Image.open(recevied_data)
            input_array = np.array(img)

            if sketch_type=="charcoal":
                
                grey_img = cv2.cvtColor(input_array, cv2.COLOR_BGR2GRAY)
                _, result = cv2.threshold(grey_img, 120, 220, cv2.THRESH_BINARY_INV)
                

            elif sketch_type=="oil":
                
                result = cv2.xphoto.oilPainting(input_array, 6, 3)

            elif sketch_type=="water":
                result = cv2.stylization(input_array, sigma_s=100, sigma_r=0.45)    

            elif sketch_type=="texture":
                sharp_img = cv2.detailEnhance(input_array,sigma_s=40,sigma_r=0.8)
                tex_gray, result = cv2.pencilSketch(sharp_img, sigma_s=10, sigma_r=0.40, shade_factor=0.02)
            
            elif sketch_type=="sharp":
                result = cv2.detailEnhance(input_array,sigma_s=40,sigma_r=0.8)
                
            
            elif sketch_type=="posterization":
                num_levels = 6
                result = cv2.cvtColor(input_array, cv2.COLOR_BGR2Lab)
                result[:, :, 1] = (result[:, :, 1] ) * num_levels
                result[:, :, 2] = (result[:, :, 2] ) * num_levels
                result = cv2.cvtColor(result, cv2.COLOR_Lab2BGR)

            elif sketch_type=="pop":
                result = cv2.cvtColor(input_array, cv2.COLOR_BGR2LAB)
                l_channel, a_channel, b_channel = cv2.split(result)
                _, a_threshold = cv2.threshold(a_channel, 128, 255, cv2.THRESH_BINARY)
                _, b_threshold = cv2.threshold(b_channel, 128, 255, cv2.THRESH_BINARY)
                pop_art_mask = cv2.bitwise_and(a_threshold, b_threshold)
                a_channel = cv2.add(a_channel, 50)
                b_channel = cv2.add(b_channel, 50)
                result = cv2.merge((l_channel, a_channel, b_channel))
                result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

            elif sketch_type=="mosiac":
                block_size = 10
                height, width = input_array.shape[:2]
                
                result = input_array.copy()
                for i in range(0, height, block_size):
                     for j in range(0, width, block_size):
                        roi = input_array[i:i+block_size, j:j+block_size]
                        avg_color = np.mean(roi, axis=(0, 1))
                        result[i:i+block_size, j:j+block_size] = avg_color
            
            
            
            elif sketch_type=="cartoon":
                #converting an image to grayscale
                ReSized1 = cv2.resize(input_array, (960, 540))
                
                grayScaleImage = cv2.cvtColor(input_array, cv2.COLOR_BGR2GRAY)
                ReSized2 = cv2.resize(grayScaleImage, (960, 540))
                smoothGrayScale = cv2.medianBlur(grayScaleImage, 5)
                ReSized3 = cv2.resize(smoothGrayScale, (960, 540))
                getEdge = cv2.adaptiveThreshold(smoothGrayScale, 255, 
  cv2.ADAPTIVE_THRESH_MEAN_C, 
  cv2.THRESH_BINARY, 9, 9)
                ReSized4 = cv2.resize(getEdge, (960, 540))
                colorImage = cv2.bilateralFilter(input_array, 9, 300, 300)
                ReSized5 = cv2.resize(colorImage, (960, 540))
                cartoonImage = cv2.bitwise_and(colorImage, colorImage, mask=getEdge)
                ReSized6 = cv2.resize(cartoonImage, (960, 540))
                result = cartoonImage

            else:
                grey_img = cv2.cvtColor(input_array, cv2.COLOR_BGR2GRAY)
                invert = cv2.bitwise_not(grey_img)
                blur = cv2.GaussianBlur(invert, (21, 21), 0)
                invertedblur = cv2.bitwise_not(blur)
                result = cv2.divide(grey_img, invertedblur, scale=200.0)    

        
        
            output_imageB = Image.fromarray(result)
            # Convert the sketch image to a base64-encoded data URI
            img_base64 = image_to_base64(output_imageB, type, None)

            response_data = {
                'image_name': "filename_without_extension" + ".png",
                'image_base64': img_base64,
            }
            return Response(response_data)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
       
      
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

