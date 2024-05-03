import sys
import os
import hashlib
import hmac
import base64
import requests
import time

# timestamp 설정
timestamp = str(int(time.time() * 1000))

access_key = ""
secret_key = ""
#secret_Key = bytes(secret_key, 'UTF-8')

api_server = "https://ncloud.apigw.ntruss.com"
api_url = "/vpc/v2/getVpcList"

url = api_server + api_url

method = "GET"
message = method + " " + url + "\n" + timestamp + "\n" + access_key
message = bytes(message, 'UTF-8')
signingKey = base64.b64encode(hmac.new(secret_key.encode('UTF-8'), message, digestmod=hashlib.sha256).digest())

header = {
    "x-ncp-apigw-timestamp": timestamp,
    "x-ncp-iam-access-key": access_key,
    "x-ncp-apigw-signature-v2": signingKey.decode('UTF-8')
}

data = {
    "vpcName": "cloit-vpc"
}

response = requests.get(url, headers=header, data=data)

print (response.text)
