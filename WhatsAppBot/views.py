# In views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
from pyzbar.pyzbar import decode
from .utils import *
from .models import UserBrowser

class QRGeneratorAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')

        if not username:
            return Response({'error': 'Please provide a username in the request body'}, status=400)

        qr_data = self.generate_qr_code(username)
        return Response({'qr_data': qr_data})

    def generate_qr_code(self, username):
        # Check if the driver exists, if not, create a new instance
        if not hasattr(self, 'driver') or self.driver is None:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=None)

            # Open WhatsApp Web
            self.driver.get('https://web.whatsapp.com')

        # Wait for the canvas element to load
        canvas_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/canvas'))
        )

        user_browser, created = UserBrowser.objects.get_or_create(username=username)
        if not created:
            # If the user already exists, update the browser_instance_id
            user_browser.browser_instance_id = self.driver.session_id
            user_browser.save()

        qr_code_data_ref = canvas_element.get_attribute("data-ref")
        canvas_element.screenshot('qr_code.png')

        # Decode QR code from the captured screenshot
        image_path = cv2.imread('qr_code.png')
        qr_data = decode_qr_code(image_path)

        return qr_data


from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
import time
class GetOpenBrowserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        browser_instance_id = request.query_params.get('browser_instance_id')

        if not (username and browser_instance_id):
            return Response({'error': 'Please provide both username and browser_instance_id as query parameters'}, status=400)

        try:
            user_browser = UserBrowser.objects.get(username=username, browser_instance_id=browser_instance_id)
        except UserBrowser.DoesNotExist:
            return Response({'error': 'User browser information not found'}, status=404)
        
        user_browser = UserBrowser.objects.get(username=username)
        browser_instance_id = user_browser.browser_instance_id

        caps = DesiredCapabilities.CHROME
        caps['goog:chromeOptions'] = {'debuggerAddress': '127.0.0.1:9222'}  # Replace with your debug address

        # Initialize WebDriver
        driver = WebDriver(command_executor='http://127.0.0.1:4444')
        
        # Attach to the existing session
        driver.attach_session(browser_instance_id, caps)
       
        first_chat = driver.find_element(By.XPATH, '//*[@id="pane-side"]/div/div/div/div[1]/div/div/div/div[2]')
        first_chat.click()

        time.sleep(10)
        return Response({'message': 'Browser instance retrieved successfully'})
