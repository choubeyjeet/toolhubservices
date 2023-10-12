from django.shortcuts import render
import numpy as np
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from io import BytesIO
from PIL import Image
import base64
import cv2

class ImageBlurFace(APIView):
    def post(self, request, format=None):
        try:
            received_data = request.FILES.get('image')
            
            if received_data:
                original_filename = received_data.name
                type = original_filename.split('.')[-1]
                img = Image.open(received_data)
                input_array = np.array(img)

                # Load the face detection classifier
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

                # Detect faces in the image
                gray = cv2.cvtColor(input_array, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                # Blur faces in the image
                for (x, y, w, h) in faces:
                    face_roi = input_array[y:y + h, x:x + w]
                    face_roi = cv2.GaussianBlur(face_roi, (23, 23), 30)
                    input_array[y:y + face_roi.shape[0], x:x + face_roi.shape[1]] = face_roi

                # Convert the modified array back to an image without changing color space
                output_image = Image.fromarray(input_array)

                filename_without_extension = original_filename.rsplit('.', 1)[0]

                # Save the modified image as PNG
                response_data = {
                    'image_name': filename_without_extension + "_blurred.png",
                    'image_base64': image_to_base64(output_image, "png"),
                }

                return Response(response_data)
            else:
                raise Http404
        except Exception as e:
            print(str(e))
            return Response("Error occurred")

def image_to_base64(image, type):
    buffered = BytesIO()
    img = image
    img.save(buffered, format=type)

    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    mime_type = f'image/{type}'

    data_uri = f'data:{mime_type};base64,{img_base64}'

    return data_uri
