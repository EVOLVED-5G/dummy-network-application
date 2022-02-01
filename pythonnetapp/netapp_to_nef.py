import requests
import json
import configparser
import redis
import os
import datetime
import re

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def register_netapp_to_nef(nef_ip, nef_port):
    access_token_url = "http://{}:{}/api/v1/login/access-token".format(nef_ip, nef_port)
    access_payload = {
        "username": "admin@my-email.com",
        "password": "pass"
    }
    response = requests.request('POST', access_token_url, data=access_payload)
    parsed = json.loads(response.text)
    access_token = parsed['access_token']
    return access_token


def monitor_subscription(nef_ip, nef_port, callback_ip, callback_port, times, access_token):
    monitoringExpireTime = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    url = "http://{}:{}/api/v1/3gpp-monitoring-event/v1/myNetapp/subscriptions".format(nef_ip, nef_port)
    payload = json.dumps({
        "externalId": "10001@domain.com",
        "notificationDestination": "http://{}:{}/callbacks".format(callback_ip, callback_port),
        "monitoringType": "LOCATION_REPORTING",
        "maximumNumberOfReports": times,
        "monitorExpireTime": monitoringExpireTime
    })

    headers = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + access_token
    }

    response = requests.request('POST', url, headers=headers, data=payload)
    parsed = json.loads(response.text)

    return parsed


def sessionqos_subscription(nef_ip, nef_port, callback_ip, callback_port, access_token):

    url = "http://{}:{}/api/v1/3gpp-as-session-with-qos/v1/myNetApp/subscriptions".format(nef_ip, nef_port)
    payload = json.dumps({
        "ipv4Addr": "10.0.0.1",
        "notificationDestination": "http://{}:{}/callbacks".format(callback_ip, callback_port),
        "snssai": {
            "sst": 1,
            "sd": "000001"
          },
          "dnn": "province1.mnc01.mcc202.gprs",
          "qosReference": 82,
          "altQoSReferences": [
            0
          ],
          "usageThreshold": {
            "duration": 0,
            "totalVolume": 0,
            "downlinkVolume": 0,
            "uplinkVolume": 0
          },
          "qosMonInfo": {
            "reqQosMonParams": [
              "DOWNLINK"
            ],
            "repFreqs": [
              "EVENT_TRIGGERED"
            ],
            "latThreshDl": 0,
            "latThreshUl": 0,
            "latThreshRp": 0,
            "waitTime": 0,
            "repPeriod": 0
          }
    })

    headers = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + access_token
    }

    response = requests.request('POST', url, headers=headers, data=payload)
    parsed = json.loads(response.text)

    return parsed


def qos_characteristics(nef_ip, nef_port, access_token):

    url = "http://{}:{}/api/v1/qosInfo/qosCharacteristics".format(nef_ip, nef_port)

    headers = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + access_token
    }

    response = requests.request('GET', url, headers=headers)
    parsed = json.loads(response.text)

    return parsed


def qos_profiles(nef_ip, nef_port, access_token):

    url = "http://{}:{}/api/v1/qosInfo/qosProfiles/AAAAA1".format(nef_ip, nef_port)

    headers = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + access_token
    }

    response = requests.request('GET', url, headers=headers)
    parsed = json.loads(response.text)

    return parsed


if __name__ == '__main__':

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )

    config = configparser.ConfigParser()
    config.read('credentials.properties')

    nef_ip = config.get("credentials", "nef_ip")
    nef_port = config.get("credentials", "nef_port")
    callback_ip = config.get("credentials", "callback_ip")
    callback_port = config.get("credentials", "callback_port")

    try:
        if not r.exists('nef_access_token'):
            nef_access_token = register_netapp_to_nef(nef_ip, nef_port)
            r.set('nef_access_token', nef_access_token)
            print("NEF Token: {}\n".format(nef_access_token))
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test Monitoring Event API? (Y/n) ")
        if ans == "Y" or ans == 'y':
            times = input("Number of location monitoring callbacks: ")
            last_response_from_nef = monitor_subscription(nef_ip, nef_port, callback_ip, callback_port, int(times), nef_access_token)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test Session-with-QoS API? (Y/n) ")
        if ans == "Y" or ans == 'y':
            last_response_from_nef = sessionqos_subscription(nef_ip, nef_port, callback_ip, callback_port, nef_access_token)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
            print("\nTo delete QoS subscription, execute the following command (inside the container):")
            sub_resource = last_response_from_nef['link']
            print("curl --request DELETE {} --header 'Authorization: Bearer {}'".format(sub_resource, nef_access_token))
            print("\nOr the following command (outside the container):")
            sub_resource_a = re.sub(r'(host.docker.internal)', 'localhost', sub_resource)
            print("curl --request DELETE {} --header 'Authorization: Bearer {}'".format(sub_resource_a, nef_access_token))
    except Exception as e:
        status_code = e.args[1]
        print(e)


    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test QoS Information APIs? (Y/n) ")
        if ans == "Y" or ans == 'y':
            last_response_from_nef = qos_characteristics(nef_ip, nef_port, nef_access_token)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
            last_response_from_nef = qos_profiles(nef_ip, nef_port, nef_access_token)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
    except Exception as e:
        status_code = e.args[1]
        print(e)
