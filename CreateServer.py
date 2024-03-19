import sys
import os
import hashlib
import hmac
import base64
import requests
import time

# unix timestamp 설정
timestamp = int(time.time() * 1000)
timestamp = str(timestamp)

# Ncloud API Key 설정
ncloud_accesskey = "C012A25AA319066052E1"
ncloud_secretkey = "CD4225BCE6E74A0268D70EAD8E7BA8E7374448A5"

# 암호화 문자열 생성을 위한 기본값 설정
apicall_method = "POST"
space = " "
new_line = "\n"

# API 서버 정보
api_server = "https://ncloud.apigw.ntruss.com"

# API URL 
api_url = "/vserver/v2/createServerInstances"

# 변수
region = "KR"
vpcno = "25726"
subnetno = "96128"
acgno = "119859"
servercount = "1"
servername = "awx-test-api"
CentOSimage = "SW.VSVR.OS.LNX64.CNTOS.0708.B050"
UbuntuOSimage = "SW.VSVR.OS.LNX64.UBNTU.SVR2004.B050" 
interface = "0"
keyname = "up-km"
privateip = "192.168.31.80"
initscript = "53064"

# hmac으로 암호화할 문자열 생성
message = apicall_method + space + api_url + new_line + timestamp + new_line + ncloud_accesskey
message = bytes(message, 'UTF-8')

# hmac_sha256 암호화
ncloud_secretkey = bytes(ncloud_secretkey, 'UTF-8')
signingKey = base64.b64encode(hmac.new(ncloud_secretkey, message, digestmod=hashlib.sha256).digest())

# http 호출 헤더값 설정
http_header = {
    'x-ncp-apigw-timestamp': timestamp,
    'x-ncp-iam-access-key': ncloud_accesskey,
    'x-ncp-apigw-signature-v2': signingKey
}

# data

data = {
     "regionCode" : region,
     "serverImageProductCode" : CentOSimage,
     "vpcNo": vpcno,
     "subnetNo": subnetno,
     "serverCreateCount" : servercount,
     "serverName" : servername,
     "networkInterfaceList.1.networkInterfaceOrder" : interface,
     "networkInterfaceList.1.accessControlGroupNoList.1" : acgno,
     "loginKeyName" : keyname,
     "networkInterfaceList.1.ip" : privateip,
     "initScriptNo" : initscript
}

# api 호출
response = requests.post(api_server + api_url, headers=http_header, data=data)

print (response.text)