import hashlib
import hmac
import base64
import requests
import time
from datetime import datetime
import json

timestamp = int(time.time() * 1000)
timestamp = str(timestamp)

get_method = "GET"
post_method = "POST"
date = datetime.today()
today = date.strftime('%y%m%d')
bot_token = ""
chat_id = ""

url = "https://ncloud.apigw.gov-ntruss.com"
info_blockstorage_url = "/vserver/v2/getBlockStorageSnapshotInstanceList"
create_snapshot_url = "/vserver/v2/createBlockStorageSnapshotInstance"
getServerInstance_url = "/vserver/v2/getServerInstanceDetail"
get_blockstorage_detail_url = "/vserver/v2/getBlockStorageInstanceDetail"
delete_snapshot_url = "/vserver/v2/deleteBlockStorageSnapshotInstances"

# 삭제되면 안 되는 이미지 목록 (exclude_ids)
exclude_ids = ["100619351", "100619357", "100619360", "100619361", "101027601", "101027600", "101027599", "101027598", "101027597", "101027596", "101027595", "101027594", "101027593", "101027592", "101027591", "101027590"]

def get_header(input_url, method):
    access_key = ""				# access key id (from portal or Sub Account)
    secret_key = ""				# secret key (from portal or Sub Account)
    secret_key = bytes(secret_key, 'UTF-8')

    message = method + " " + input_url + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())


    http_header = {
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': access_key,
        'x-ncp-apigw-signature-v2': signingKey
    }

    return http_header

# 텔레그램 webhook
def web_hook(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

header = get_header(f'{info_blockstorage_url}?responseFormatType=json&regionCode=KRS', get_method)
snapshot_info = requests.get(f'{url}{info_blockstorage_url}?responseFormatType=json&regionCode=KRS', headers=header)
sn_info = snapshot_info.json()

volum_no = []
create_list = []
fail_list = []
fail_reson = []
create_snapshot_ids = []

# 현재 스냅샷 목록에서 제외할 이미지를 제외하고 리스트 생성

for volum in sn_info['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']:
    volum_no_value = volum['originalBlockStorageInstanceNo']
    
    # exclude_ids에 포함되지 않으면 리스트에 추가
    if volum['blockStorageSnapshotInstanceNo'] not in exclude_ids:
    # 이미 volum_no에 존재하는 값은 추가하지 않도록 체크
        if volum_no_value not in volum_no:
            volum_no.append(volum_no_value)
        else:
            print(f"블록스토리지 ID {volum_no_value}는 이미 목록에 존재하여 추가되지 않았습니다.")
        #volum_no.append(volum_no_value)
    else:
        print(f"스냅샷 ID {volum['blockStorageSnapshotInstanceNo']}는 제외된 ID로, 리스트에 추가되지 않음.")

print("현재 volum_no 리스트:", volum_no)


# 삭제할 스냅샷 ID 리스트
delete_snapshot_ids = []

# 기존 스냅샷 목록에서 삭제할 ID 찾기
for snapshot in sn_info['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']:
    snapshot_id = snapshot['blockStorageSnapshotInstanceNo']

    # 제외할 ID 목록에 포함되지 않는 경우에만 삭제 리스트에 추가
    if snapshot_id not in exclude_ids and snapshot_id not in create_snapshot_ids:
        delete_snapshot_ids.append(snapshot_id)

# 삭제할 스냅샷 ID 목록 출력
print("삭제할 스냅샷 ID 목록:")
print(delete_snapshot_ids)


# 삭제되지 않도록 제외할 이미지를 제외한 나머지 이미지만 처리
'''
for num, value in enumerate(volum_no):
    # 제외할 이미지가 아닌 경우에만 삭제 작업 진행
    if value not in exclude_ids:  # 삭제되지 않도록 설정된 이미지는 제외
        header = get_header(f'{get_blockstorage_detail_url}?regionCode=KRS&blockStorageInstanceNo={value}&responseFormatType=json', get_method)
        detail_volume = requests.get(f'{url}{get_blockstorage_detail_url}?regionCode=KRS&blockStorageInstanceNo={value}&responseFormatType=json', headers=header)
        detail_volume_info = detail_volume.json()
        server_no = detail_volume_info['getBlockStorageInstanceDetailResponse']['blockStorageInstanceList'][0]['serverInstanceNo']

        header = get_header(f'{getServerInstance_url}?regionCode=KRS&serverInstanceNo={server_no}&responseFormatType=json', get_method)
        detail_server = requests.get(f'{url}{getServerInstance_url}?regionCode=KRS&serverInstanceNo={server_no}&responseFormatType=json', headers=header)
        server_info = detail_server.json()
        server_name = server_info['getServerInstanceDetailResponse']['serverInstanceList'][0]['serverName']

        # 스냅샷 생성 데이터
        data = {
            "originalBlockStorageInstanceNo": value,
            "blockStorageSnapshotName": f'{server_name}-{today}',
            "regionCode": 'KRS'
        }

        print(f"생성 요청 데이터: {json.dumps(data, indent=2)}")
        '''

        # 스냅샷 생성 요청
        #header = get_header(create_snapshot_url, post_method)
        #create_snapshot = requests.post(f'{url}{create_snapshot_url}', headers=header, data=data)


        #if create_snapshot.status_code == 200:       
        #    print("생성 요청 성공:", server_name)
        #    create_list.append(server_name)
        #else:
        #    print("생성 요청 실패:", server_name)
        #    fail_list.append(server_name)
        #    fail_reson.append(create_snapshot.text)
        #    print(create_snapshot.text)
        #print("-------------------------------------")

#######삭제##########

# 삭제할 스냅샷을 생성하지 않은 것들만 삭제

#for value in delete_snapshot_ids:
for index, value in enumerate(delete_snapshot_ids, start=1):
    delete_data = {
        f"blockStorageSnapshotInstanceNoList.{index}": value,
        #"blockStorageSnapshotInstanceNoList": value,
        #"regionCode": "KR"
    }

    print(f"삭제 요청 데이터: {json.dumps(delete_data, indent=2)}")
    print("=====================================================")

    header = get_header(delete_snapshot_url, post_method)
    delete_snapshot = requests.post(f'{url}{delete_snapshot_url}', headers=header, data=delete_data)

    if delete_snapshot.status_code == 200:
        print(f"스냅샷 {value} 삭제 성공")
    else:
        print(f"스냅샷 {value} 삭제 실패")
        print(f"응답 본문: {delete_snapshot.text}")
        fail_reson.append(f"삭제 실패: {value}")

# 실패 목록을 파일에 저장
def save_list_to_file(file_name, list_to_save):
    with open(file_name, 'w') as file:
        for item in list_to_save:
            file.write(f"{item}\n")

save_list_to_file(f'ncp(vpc)fail-{today}', fail_reson)

a = len(create_list)
b = len(fail_list)

# 성공 메시지와 실패 메시지 작성
success_message = f'NCP Snapshot 생성\n 성공 대수 : {a}\n 성공 서버 : {create_list} '
fail_message = f'NCP Snapshot 생성\n성공 대수 : {a}\n실패 대수 : {b}\n실패 서버 : {fail_list}\n'

# 텔레그램 메시지 전송
if fail_list:
    response = web_hook(bot_token, chat_id, message=fail_message)
else:
    response = web_hook(bot_token, chat_id, message=success_message)
