import requests
import json
import configparser
import redis
import os

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def register_netapp_to_capif(capif_ip, capif_port, username, password, role, description):
    url = "http://{}:{}/register".format(capif_ip, capif_port)

    payload = dict()
    payload['username'] = username
    payload['password'] = password
    payload['role'] = role
    payload['description'] = description

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_payload = json.loads(response.text)
        return response_payload['id']
    except requests.exceptions.HTTPError as err:
        raise Exception(err.response.text, err.response.status_code)


def get_capif_token(capif_ip, capif_port, username, password, role):
    url = "http://{}:{}/gettoken".format(capif_ip, capif_port)

    payload = dict()
    payload['username'] = username
    payload['password'] = password
    payload['role'] = role

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_payload = json.loads(response.text)
        return response_payload['access_token']
    except requests.exceptions.HTTPError as err:
        raise Exception(err.response.text, err.response.status_code)


def onboard_netapp_to_capif(capif_ip, capif_port, jwt_token):
    url = 'http://{}:{}/api-invoker-management/v1/onboardedInvokers'.format(capif_ip, capif_port)

    payload = open('invoker_details.json', 'rb')

    headers = {
        'Authorization': 'Bearer {}'.format(jwt_token),
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        response_payload = json.loads(response.text)
        return response_payload['apiInvokerId']
    except requests.exceptions.HTTPError as err:
        raise Exception(err.response.text, err.response.status_code)


def discover_service_apis(capif_ip, capif_port, api_invoker_id, jwt_token):
    url = "http://{}:{}/service-apis/v1/allServiceAPIs?api-invoker-id={}".format(capif_ip, capif_port, api_invoker_id)

    payload = {}
    files = {}
    headers = {
        'Authorization': 'Bearer {}'.format(jwt_token),
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload, files=files)
        response.raise_for_status()
        response_payload = json.loads(response.text)
        return response_payload
    except requests.exceptions.HTTPError as err:
        message = json.loads(err.response.text)
        status = err.response.status_code
        raise Exception(message, status)


if __name__ == '__main__':

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )

    config = configparser.ConfigParser()
    config.read('credentials.properties')

    username = config.get("credentials", "invoker_username")
    password = config.get("credentials", "invoker_password")
    role = config.get("credentials", "invoker_role")
    description = config.get("credentials", "invoker_description")
    capif_ip = config.get("credentials", "capif_ip")
    capif_port = config.get("credentials", "capif_port")

    try:
        if not r.exists('netappID'):
            netappID = register_netapp_to_capif(capif_ip, capif_port, username, password, role, description)
            r.set('netappID', netappID)
            print("NetAppID: {}\n".format(netappID))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 409:
            print("User already registed. Continue with token request\n")
        else:
            print(e)

    try:
        if not r.exists('capif_access_token'):
            capif_access_token = get_capif_token(capif_ip, capif_port, username, password, role)
            r.set('capif_access_token', capif_access_token)
            print("Capif Token: {}\n".format(capif_access_token))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 401:
            print("Bad credentials. User not found\n")
        else:
            print(e)
        capif_access_token = None

    try:
        if not r.exists('invokerID'):
            capif_access_token = r.get('capif_access_token')
            invokerID = onboard_netapp_to_capif(capif_ip, capif_port, capif_access_token)
            r.set('invokerID', invokerID)
            print("ApiInvokerID: {}\n".format(invokerID))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 401:
            capif_access_token = get_capif_token(capif_ip, capif_port, username, password, role)
            r.set('capif_access_token', capif_access_token)
            print("New Capif Token: {}\n".format(capif_access_token))
            invokerID = onboard_netapp_to_capif(capif_ip, capif_port, capif_access_token)
            r.set('invokerID', invokerID)
            print("ApiInvokerID: {}\n".format(invokerID))
        elif status_code == 403:
            print("Invoker already registered.")
            print("Chanage invoker public key in invoker_details.json\n")
        else:
            print(e)

    try:
        if r.exists('invokerID'):
            invokerID = r.get('invokerID')
            capif_access_token = r.get('capif_access_token')
            discovered_apis = discover_service_apis(capif_ip, capif_port, invokerID, capif_access_token)
            print("Discovered APIs")
            print(json.dumps(discovered_apis, indent=2))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 401:
            capif_access_token = get_capif_token(capif_ip, capif_port, username, password, role)
            r.set('capif_access_token', capif_access_token)
            print("New Capif Token: {}\n".format(capif_access_token))
            invokerID = r.get('invokerID')
            discovered_apis = discover_service_apis(capif_ip, capif_port, invokerID, capif_access_token)
            print(json.dumps(discovered_apis, indent=2))
        elif status_code == 403:
            print("API Invoker does not exist. API Invoker id not found")
        else:
            print(e)