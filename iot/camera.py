#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pip3 install paho-mqtt,picamera,requests
from picamera import PiCamera
import time
import random
import base64
import requests
import json
import hashlib
import datetime
import hmac
import paho.mqtt.client as mqtt
import configparser

config = configparser.ConfigParser()
config.read('iot.cfg')

# IoT
PRODUCT_KEY = config['IOT']['productKey']
DEVICE_NAME = config['IOT']['deviceName']
DEVICE_SECRET = config['IOT']['deviceSecret']

HOST = PRODUCT_KEY + '.iot-as-mqtt.cn-shanghai.aliyuncs.com'
PUB_TOPIC = "/sys/" + PRODUCT_KEY + "/" + DEVICE_NAME + "/thing/event/property/post";
#aliyun auth
ALIYUN_AK = config['aliyun']['accessKeyId']
ALIYUN_AK_SECRET = config['aliyun']['accessKeySecret']

camera = PiCamera()
camera.resolution = (720, 480)

def hmacsha1(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()

def getAliyunIoTClient(productKey, deviceName, deviceSecret):
    timestamp = str(int(time.time()))
    CLIENT_ID = "paho.py|securemode=3,signmethod=hmacsha1,timestamp=" + timestamp + "|"
    CONTENT_STR_FORMAT = "clientIdpaho.pydeviceName" + deviceName + "productKey" + productKey + "timestamp" + timestamp# set username / password.
    USER_NAME = deviceName + "&" + productKey
    PWD = hmacsha1(deviceSecret, CONTENT_STR_FORMAT)
    client = mqtt.Client(client_id = CLIENT_ID, clean_session = False)
    client.username_pw_set(USER_NAME, PWD)
    return client

client = getAliyunIoTClient(PRODUCT_KEY,DEVICE_NAME,DEVICE_SECRET)

def makeDataplusSignature(bodyStr, date):
    md5Body = md5_base64(bodyStr)
    stringToSign = "POST\napplication/json\n" + md5Body + "\napplication/json\n" + date + "\n/face/attribute"
    sign = hmacsha1_base64(ALIYUN_AK_SECRET, stringToSign)
    return "Dataplus " + ALIYUN_AK + ":" + sign

def get_current_date():
    return datetime.datetime.strftime(datetime.datetime.utcnow(), "%a, %d %b %Y %H:%M:%S GMT")

def hmacsha1_base64(key, msg):
    digest = hmac.new(key.encode(), msg.encode(), hashlib.sha1).digest()
    return str(base64.b64encode(digest), 'utf-8')

def md5_base64(strBody):
    hash = hashlib.md5()
    hash.update(strBody.encode())
    return str(base64.b64encode(hash.digest()), 'utf-8')


def getImgBase64(filePath):
    f = open(filePath, 'rb')
    data = f.read()
    imgBase64str = base64.b64encode(data)
    return str(imgBase64str, 'utf-8')

def getFaceAttribute(filePath):
    print('Face Attribute src=' + filePath)
    date = get_current_date();
    imgBase64str = getImgBase64(filePath)
    payload = {
        'type': 1,
        'content': imgBase64str
    }
    sign = makeDataplusSignature(json.dumps(payload, separators = (',', ':')), date)
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'date': date,
        'authorization': sign
    }
    url = 'https://dtplus-cn-shanghai.data.aliyuncs.com/face/attribute'
    r = requests.post(url, headers = headers, data = json.dumps(payload, separators = (',', ':')))
    rtData = r.json()

    if rtData['face_num'] > 0:
        for index in range(len(rtData['gender'])):
            payload_json = {
                'id': int(time.time()),
                'params': {
                    'gender': 'f'
                    if rtData['gender'][index] == 0
                    else 'm',
                    'age': rtData['age'][index],
                    'glass': 'n'
                    if rtData['glass'][index] == 0
                    else 'y'
                },
                'method': "thing.event.property.post"
            }
            print('send data to iot server: ' + str(payload_json))
            client.publish(PUB_TOPIC, payload = str(payload_json))



# Take a photo first, then upload photo to oss
def take_photo():

    ticks = int(time.time())
    fileName = 'raspi%s.jpg' % ticks
    filePath = '/home/pi/iot/photos/%s' % fileName
    try: 
        #take a photo
        camera.capture(filePath)
        # face recognition
        getFaceAttribute(filePath)
    finally:
        print('finally ')


if __name__ == '__main__':

    client.connect(host = HOST, port = 1883, keepalive = 300)
    while True:
        time.sleep(10)
        take_photo()
