from django.urls import path
from .views import *

urlpatterns = [
    path('generate_qr/', QRGeneratorAPIView.as_view(), name='generate_qr'),
    # path('open_browser/', GetOpenBrowserAPIView.as_view(), name='open_browser'),
]