import requests
import json
import configparser
import redis
import os

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def register_netapp_to_capif(username, password, role, description):
    url = "http://host.docker.internal:8080/register"

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


def get_capif_token(username, password, role):
    url = "http://host.docker.internal:8080/gettoken"

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


def onboard_netapp_to_capif(jwt_token):
    url = 'http://host.docker.internal:8080/api-invoker-management/v1/onboardedInvokers'

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


def discover_service_apis(api_invoker_id, jwt_token):
    url = "http://host.docker.internal:8080/service-apis/v1/allServiceAPIs?api-invoker-id={}".format(api_invoker_id)

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
    config.read('netapp.properties')

    username = config.get("credentials", "username")
    password = config.get("credentials", "password")
    role = config.get("credentials", "role")
    description = config.get("credentials", "description")

    try:
        if not r.exists('netappID'):
            netappID = register_netapp_to_capif(username, password, role, description)
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
            capif_access_token = get_capif_token(username, password, role)
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
            invokerID = onboard_netapp_to_capif(capif_access_token)
            r.set('invokerID', invokerID)
            print("ApiInvokerID: {}\n".format(invokerID))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 401:
            capif_access_token = get_capif_token(username, password, role)
            r.set('capif_access_token', capif_access_token)
            print("New Capif Token: {}\n".format(capif_access_token))
            invokerID = onboard_netapp_to_capif(capif_access_token)
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
            discovered_apis = discover_service_apis(invokerID, capif_access_token)
            print("Discovered APIs")
            print(json.dumps(discovered_apis, indent=2))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 401:
            capif_access_token = get_capif_token(username, password, role)
            r.set('capif_access_token', capif_access_token)
            print("New Capif Token: {}\n".format(capif_access_token))
            invokerID = r.get('invokerID')
            discovered_apis = discover_service_apis(invokerID, capif_access_token)
            print(json.dumps(discovered_apis, indent=2))
        elif status_code == 403:
            print("API Invoker does not exist. API Invoker id not found")
        else:
            print(e)