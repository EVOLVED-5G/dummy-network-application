from dis import dis
import requests
import json
import configparser
import redis
import os

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

def check_auth_to_aef(capif_ip, capif_port):
    #url = "https://{}/{}{}".format(capif_ip, ccf_url, api_invoker_id)

    print("Try to use AEF API")
    #url = "https://python_aef:8085/check-authentication"
    url = "https://{}:{}/check-authentication".format(capif_ip, capif_port)

    payload = {
        "apiInvokerId": "",
        "supportedFeatures": ""

    }

    files = {}
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        print("''''''''''REQUEST'''''''''''''''''")
        print("Request: to ",url) 
        print("Request Headers: ",  headers) 
        print("''''''''''REQUEST'''''''''''''''''")
        response = requests.request("POST", url, headers=headers, data=payload, files=files, cert=('dummy.crt', 'private.key'), verify=False)
        response.raise_for_status()
        response_payload = json.loads(response.text)
        print("''''''''''RESPONSE'''''''''''''''''")
        print("Response to: ",response.url) 
        print("Response Headers: ",  response.headers) 
        print("Response: ", response.json())
        print("Response Status code: ", response.status_code)
        print("Success to obtain auth of AEF")
        print("''''''''''RESPONSE'''''''''''''''''")
        return response_payload
    except requests.exceptions.HTTPError as err:
        print(err.response.text)
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
    cn = config.get("credentials", "invoker_cn")

    # capif_ip = config.get("credentials", "capif_ip")
    # capif_port = config.get("credentials", "capif_port")

    capif_ip = os.getenv('CAPIF_HOSTNAME')
    capif_port = os.getenv('CAPIF_PORT')

    capif_callback_ip = config.get("credentials", "capif_callback_ip")
    capif_callback_port = config.get("credentials", "capif_callback_port")


    try:
        if r.exists('invokerID'):
            print("Going to check auth to AEF")
            invokerID = r.get('invokerID')
            capif_access_token = r.get('capif_access_token')
            ccf_discover_url = r.get('ccf_discover_url')
            aef_ip_check = r.get("demo_ipv4_addr_check")
            aef_port_check = r.get("demo_port_check")
            discovered_apis = check_auth_to_aef(aef_ip_check, aef_port_check)
            r.set("jwt_token", discovered_apis["access_token"])
            print("Invoker Authrized to use AEF")
            print(json.dumps(discovered_apis, indent=2))

    except Exception as e:
        status_code = e.args[0]
        if status_code == 401:
            print("API Invoker is not authorized")
        elif status_code == 403:
            print("API Invoker does not exist. API Invoker id not found")
        else:
            print(e)