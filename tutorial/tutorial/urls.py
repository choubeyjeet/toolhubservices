"""
URL configuration for tutorial project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from quickstart.Image.ImageRemoveBackground import ImageRemoveBackground
from quickstart.Image.ImageToSketch import ImageToSketch
from quickstart.Pdf.PdftoDocxConverter import PdftoDocxConverter
from quickstart.Pdf.PdfDownload import DownloadPDF
from quickstart.Pdf.PdftoJpegConverter import PdftoJpegConverter
from quickstart.Pdf.PdfEdit.PdfEditBase64ToImg import PdfEditBase64ToImg
from quickstart.Image.ImageToPdf import ImageToPdf
urlpatterns = [
    path('admin/', admin.site.urls),
    path('removebg', ImageRemoveBackground.as_view(),name='ImageRemoveBackground'),
    path('sketch', ImageToSketch.as_view(),name='ImageToSketch'),
    path('pdf/convert', PdftoDocxConverter.as_view(),name='PdftoDocxConverter'),
    path('pdf/download', DownloadPDF.as_view(),name='DownloadPDF'),
    path('pdf/jpeg', PdftoJpegConverter.as_view(),name='PdftoJpegConverter'),
    path('pdf/edit/basetoimg', PdfEditBase64ToImg.as_view(),name='PdfEditBase64ToImg'),
    path('image/pdf', ImageToPdf.as_view(),name='ImageToPdf'),
]
