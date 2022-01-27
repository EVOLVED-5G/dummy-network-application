import requests
import json
import configparser
import redis
import os
import datetime

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
        "notificationDestination": "http://{}:{}/monitoringcallback".format(callback_ip, callback_port),
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


if __name__ == '__main__':

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )

    config = configparser.ConfigParser()
    config.read('nef.properties')

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
        times = input("Number of location monitoring callbacks: ")
        last_response_from_nef = monitor_subscription(nef_ip, nef_port, callback_ip, callback_port, int(times), nef_access_token)
        r.set('last_response_from_nef', str(last_response_from_nef))
        print("{}\n".format(last_response_from_nef))
    except Exception as e:
        status_code = e.args[1]
        print(e)
