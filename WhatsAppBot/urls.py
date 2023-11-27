from django.urls import path
from .views import *

urlpatterns = [
    path('generate_qr/', QRGeneratorAPIView.as_view(), name='generate_qr'),
    # path('open_browser/', GetOpenBrowserAPIView.as_view(), name='open_browser'),
    path('get_contact_list/', GetContactsAPIView.as_view(), name='get_contact_list'),
    path('get_specific_contact_chat/', SpecificContactChatAPIView.as_view(), name='get_specific_contact_chat'),
    path('send_message/', SendMessageAPIView.as_view(), name='send_message'),
    path('active_session/', ActiveChromeSessionAPIView.as_view(), name='active_session'),
    path('logout_whastapp/', LogoutAPIView.as_view(), name='logout_whastapp'),



]