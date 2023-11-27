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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchWindowException
import time



browser_instances = {}

class QRGeneratorAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')

        if not username:
            return Response({'error': 'Please provide a username in the request body'}, status=400)

        qr_data = self.generate_qr_code(username)
        return Response({'qr_data': qr_data})
    
    def generate_qr_code(self, username):
        try:
            # Check if the user already exists
            user_browser, created = UserBrowser.objects.get_or_create(username=username)

            # Create a new browser instance every time the QR code is generated
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=None)
            
            # Open WhatsApp Web
            driver.get('https://web.whatsapp.com')

            # Wait for the canvas element to load
            canvas_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/canvas'))
            )

            canvas_element.screenshot('qr_code.png')

            image_path = cv2.imread('qr_code.png')
            qr_data = decode_qr_code(image_path)

            # Update or create the UserBrowser object with the new session ID
            user_browser.browser_instance_id = driver.session_id
            user_browser.save()
            browser_instances[(username, user_browser.browser_instance_id)] = driver

            return qr_data
        except NoSuchWindowException:
             return "Window is closed. Please open the browser window and try again."


    # def generate_qr_code(self, username):
    #     try:
    #         user_browser, created = UserBrowser.objects.get_or_create(username=username)
    #         if not created:
    #             browser_instance_id = user_browser.browser_instance_id
    #             print(browser_instance_id, 'browser_instance')
    #             if (username, browser_instance_id) not in browser_instances:
    #                 # options = Options()
    #                 driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=None)
    #                 browser_instances[(username, browser_instance_id)] = driver

    #             else:
    #                 driver = browser_instances[(username, browser_instance_id)]

    #             # if not self.is_browser_session_active(driver):
    #             #     # If not active, generate a new browser_instance_id
    #             #     user_browser.browser_instance_id = driver.session_id # Generate a new browser_instance_id
    #             #     user_browser.save()
    #             #     browser_instances[(username, user_browser.browser_instance_id)] = driver
    #             #     driver.get('https://web.whatsapp.com')   
    #         else:
    #             # options = Options()
    #             driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=None)
    #             user_browser.browser_instance_id = driver.session_id # Generate a new browser_instance_id
    #             user_browser.save()
    #             browser_instances[(username, user_browser.browser_instance_id)] = driver

    #         # Open WhatsApp Web
    #         driver.get('https://web.whatsapp.com')

    #         # Wait for the canvas element to load
    #         canvas_element = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/canvas'))
    #         )

    #         canvas_element.screenshot('qr_code.png')

    #         image_path = cv2.imread('qr_code.png')
    #         qr_data = decode_qr_code(image_path)

    #         return qr_data
    #     except NoSuchWindowException:
    #          return "Window is closed. Please open the browser window and try again."
        

    # def is_browser_session_active(self, driver):
    #     try:
    #         driver.title
    #         return True
    #     except NoSuchWindowException:
    #         return False


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

        key = (username, browser_instance_id)
        print(key, 'key')

        # Assume that 'browser_instances' is the dictionary storing WebDriver instances
        if key not in browser_instances or browser_instances[key] is None:
            return Response({'error': 'WebDriver instance not found'}, status=404)

        driver = browser_instances[key]

        # Assume that 'self.driver' is the WebDriver instance created earlier
        first_chat_xpath = '//*[@id="pane-side"]/div/div/div/div[1]/div/div/div/div[2]'
        try:
            first_chat = driver.find_element(By.XPATH, first_chat_xpath)
            print(first_chat, 'chat____')
            first_chat.click()
            messages = driver.find_elements(By.XPATH, '//*[@id="main"]/div[2]/div/div[2]/div[3]')
            print(messages, 'msg')
            # Print the messages to the console
            for message in messages:
                message_text = message.text
                print(message_text, 'test')
        except:
            return Response({'error': 'First chat not found'}, status=404)

        time.sleep(10)
        return Response({'message': 'Browser instance retrieved successfully'})




class GetContactsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        browser_instance_id = request.query_params.get('browser_instance_id')

        if not (username and browser_instance_id):
            return Response({'error': 'Please provide both username and browser_instance_id as query parameters'}, status=400)

        try:
            user_browser = UserBrowser.objects.get(username=username, browser_instance_id=browser_instance_id)
        except UserBrowser.DoesNotExist:
            return Response({'error': 'User browser information not found'}, status=404)

        key = (username, browser_instance_id)

        if key not in browser_instances or browser_instances[key] is None:
            return Response({'error': 'WebDriver instance not found'}, status=404)

        driver = browser_instances[key]

        try:
            contacts = self.get_first_ten_contacts(driver)
            return Response({'all_contacts': contacts})
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def get_first_ten_contacts(self, driver):
        try:
            container_xpath = '/html/body/div[1]/div/div/div[4]/div/div[2]/div/div/div'
            chats_container = driver.find_element(By.XPATH, container_xpath)

            single_chats = []
            group_chats = []

            max_index = 10  
            
            for index in range(1, max_index + 1):
                single_chat_xpath = f'//*[@id="pane-side"]/div/div/div/div[{index}]/div/div/div/div[2]/div[1]/div[1]/div/span'
                group_chat_xpath = f'//*[@id="pane-side"]/div/div/div/div[{index}]/div/div/div/div[2]/div[1]/div[1]/span'
                
                single_chat_elements = chats_container.find_elements(By.XPATH, single_chat_xpath)
                single_chats.extend(single_chat_elements)
                
                group_chat_elements = chats_container.find_elements(By.XPATH, group_chat_xpath)
                group_chats.extend(group_chat_elements)
            
            single_chat_names = [chat.text for chat in single_chats]
            group_chat_names = [chat.text for chat in group_chats]

            all_contacts = []
            all_contacts.extend(single_chat_names)
            all_contacts.extend(group_chat_names)

            return all_contacts
        except Exception as e:
            raise e



class SpecificContactChatAPIView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        browser_instance_id = request.query_params.get('browser_instance_id')
        contact_name = request.query_params.get('contact_name') 

        if not (username and browser_instance_id):
            return Response({'error': 'Please provide both username and browser_instance_id as query parameters'}, status=400)
        
        if not contact_name:
            return Response({'error': 'Please provide the contact_name as a query parameter'}, status=400)
        
        try:
            user_browser = UserBrowser.objects.get(username=username, browser_instance_id=browser_instance_id)
        except UserBrowser.DoesNotExist:
            return Response({'error': 'User browser information not found'}, status=404)

        key = (username, browser_instance_id)

        if key not in browser_instances or browser_instances[key] is None:
            return Response({'error': 'WebDriver instance not found'}, status=404)

        driver = browser_instances[key] 

        try:
            chat = self.get_contact_chat(driver, contact_name)
            return Response({'contact_chat': chat})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def get_contact_chat(self, driver, contact_name):

        try:
            contact_xpath = f'//span[@title="{contact_name}"]'
            contact_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, contact_xpath))
            )
            contact_element.click()
            messages = driver.find_elements(By.XPATH, '//*[@id="main"]/div[2]/div/div[2]/div[3]')
            print(messages, 'msg')
            for message in messages:
                message_text = message.text
                print(message_text, 'test')


            chat_texts = [message.text for message in messages]
            print(chat_texts, 'txtx____xtxtx')
            chat = '\n'.join(chat_texts)
            print(chat)

            return chat
        except Exception as e:
            raise e


class SendMessageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        browser_instance_id = request.data.get('browser_instance_id')
        contact_name = request.data.get('contact_name')
        message = request.data.get('message')

        if not (username and browser_instance_id and contact_name and message):
            return Response({'error': 'Please provide username, browser_instance_id, contact_name, and message in the request'}, status=400)
        
        try:
            user_browser = UserBrowser.objects.get(username=username, browser_instance_id=browser_instance_id)
        except UserBrowser.DoesNotExist:
            return Response({'error': 'User browser information not found'}, status=404)

        key = (username, browser_instance_id)

        if key not in browser_instances or browser_instances[key] is None:
            return Response({'error': 'WebDriver instance not found'}, status=404)

        driver = browser_instances[key]

        try:
            sent = self.send_message(driver, contact_name, message)
            if sent:
                return Response({'message': 'Message sent successfully'})
            else:
                return Response({'error': 'Failed to send message'}, status=500)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def send_message(self, driver, contact_name, message):
        try:
            contact_xpath = f'//span[@title="{contact_name}"]'
            contact_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, contact_xpath))
            )
            contact_element.click()

            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]//div[@contenteditable="true"]'))
            )

            input_box.send_keys(message)
            input_box.send_keys(Keys.ENTER)

            return True
        except Exception as e:
            raise e



class ActiveChromeSessionAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve active Chrome sessions
        active_sessions = self.get_active_chrome_sessions()
        return Response({'active_sessions': active_sessions})

    def get_active_chrome_sessions(self):
        active_sessions = []

        # Iterate through stored browser instances to check if they are active
        for key, driver in browser_instances.items():
            username, browser_instance_id = key
            if self.is_browser_session_active(driver):
                active_sessions.append({'username': username, 'browser_instance_id': browser_instance_id})

        return active_sessions

    def is_browser_session_active(self, driver):
        try:
            driver.title  
            return True
        except Exception:
            return False



class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        browser_instance_id = request.data.get('browser_instance_id')

        if not (username and browser_instance_id):
            return Response({'error': 'Please provide username and browser_instance_id in the request'}, status=400)

        try:
            user_browser = UserBrowser.objects.get(username=username, browser_instance_id=browser_instance_id)
        except UserBrowser.DoesNotExist:
            return Response({'error': 'User browser information not found'}, status=404)

        key = (username, browser_instance_id)

        if key not in browser_instances or browser_instances[key] is None:
            return Response({'error': 'WebDriver instance not found'}, status=404)

        driver = browser_instances[key]

        try:
            self.logout(driver)
            driver.quit()
            return Response({'message': 'Logged out successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def logout(self, driver):
        try:
            menu_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[4]/header/div[2]/div/span/div[6]/div/span'))
            )
            menu_button.click()

            time.sleep(5)

            # Click on the logout button from the menu
            logout_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[4]/header/div[2]/div/span/div[6]/span/div/ul/li[10]/div'))
            )
            logout_button.click()
            time.sleep(5)

            
            final_logut = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[3]/div/button[2]'))
            )
            final_logut.click()
            return True
        except Exception as e:
            raise e
