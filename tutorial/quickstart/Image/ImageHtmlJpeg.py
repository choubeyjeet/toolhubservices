import logging
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

from deoldify import device
from deoldify.visualize import *
import warnings
import uuid

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .* set is empty.*?")

# Initialize DeOldify colorizer
colorizer = get_image_colorizer(artistic=True)

class ImageHtmlJpeg(APIView):
    def post(self, request, format=None):
        try:
            data = json.loads(request.body)
            url = data.get('url')
           
          
            if url:
                converted_filename = f"{uuid.uuid4().hex}.png"

                # Define the output ZIP file path
                output_path = os.path.join("files", converted_filename)

                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--headless")
                driver  = webdriver.Chrome(options=chrome_options)
                driver.maximize_window()
                driver.get(url)
                width = 1920
                height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight,document.documentElement.offsetHeight);")
                driver.set_window_size(width, height)
                driver.find_element(By.TAG_NAME, "body").screenshot(output_path)
                driver.quit()


                
                
               

                # Convert the image to base64
               

                return JsonResponse({"path": converted_filename})
            else:
                raise Http404
        except Exception as e:
            
            return Response("Error occurred")

        # finally:
        #     driver.quit()