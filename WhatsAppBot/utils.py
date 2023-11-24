import cv2
from pyzbar.pyzbar import decode

def decode_qr_code(image_path):
    gray_image = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)
    decoded_objects = decode(gray_image)
    qr_data = decoded_objects[0].data.decode('utf-8')
    return qr_data
