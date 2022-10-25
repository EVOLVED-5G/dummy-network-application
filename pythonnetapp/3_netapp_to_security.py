from dis import dis
from email import charset
import requests
import json
import configparser
import redis
import os
from termcolor import colored
# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

def register_security_service(capif_ip, api_invoker_id, jwt_token, ccf_url):

    print("HELOOO")
    #url = "https://{}/{}{}".format(capif_ip, ccf_url, api_invoker_id)
    url = "https://{}/capif-security/v1/trustedInvokers/{}".format(capif_ip, api_invoker_id)

    with open('security_info.json', "rb") as f:
        payload = json.load(f)
    #print("HELOOO")
    print(payload)

    files = {}
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        print(colored("''''''''''REQUEST'''''''''''''''''","blue"))
        print(colored(f"Request: to {url}","blue"))
        print(colored(f"Request Headers: {headers}", "blue"))
        print(colored(f"''''''''''REQUEST'''''''''''''''''", "blue"))

        response = requests.put(url, json=payload, cert=('dummy.crt', 'private.key'), verify='ca.crt')
        response.raise_for_status()
        response_payload = response.json()

        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))
        print(colored(f"Response to: {response.url}","green"))
        print(colored(f"Response Headers: {response.headers}","green"))
        print(colored(f"Response: {response.json()}","green"))
        print(colored(f"Response Status code: {response.status_code}","green"))
        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))

        return response_payload
    except requests.exceptions.HTTPError as err:
        print(err.response.text)
        message = json.loads(err.response.text)
        status = err.response.status_code
        raise Exception(message, status)

def get_security_service(capif_ip, api_invoker_id, jwt_token, ccf_url):

    #url = "https://{}/{}{}".format(capif_ip, ccf_url, api_invoker_id)
    url = "https://{}/capif-security/v1/trustedInvokers/{}".format(capif_ip, api_invoker_id)

    #payload = open('security_info.json', "rb")
    files = {}
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        print(colored("''''''''''REQUEST'''''''''''''''''","blue"))
        print(colored(f"Request: to {url}","blue"))
        print(colored(f"Request Headers: {headers}", "blue"))
        print(colored(f"''''''''''REQUEST'''''''''''''''''", "blue"))

        response = requests.request("GET", url, headers=headers, files=files, cert=('dummy.crt', 'private.key'), verify='ca.crt')
        response.raise_for_status()
        response_payload = json.loads(response.text)

        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))
        print(colored(f"Response to: {response.url}","green"))
        print(colored(f"Response Headers: {response.headers}","green"))
        print(colored(f"Response: {response.json()}","green"))
        print(colored(f"Response Status code: {response.status_code}","green"))
        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))

        return response_payload
    except requests.exceptions.HTTPError as err:
        print(err.response.text)
        message = json.loads(err.response.text)
        status = err.response.status_code
        raise Exception(message, status)


def get_security_token(capif_ip, api_invoker_id, jwt_token, ccf_url):

    #url = "https://{}/{}{}".format(capif_ip, ccf_url, api_invoker_id)
    url = "https://{}/capif-security/v1/securities/{}/token".format(capif_ip, api_invoker_id)
    #url = "https://capifcore/capif-security/v1/securities/b0bca87c72b5f2595c41ff979a6207/token"

    files = {}
    data ={
        "grant_type": "client_credentials",
        "client_id": "29f1107e089f5a95ae57826d85f4ef",
        "client_secret": "string",
        "scope": "3gpp#ec2b554166ca9c7b6c75250956f302:dummy-aef"
    }

    access_token_req = {
  "grant_type" : "client_credentials",
  "scope" : "scope",
  "client_secret" : "client_secret",
  "client_id" : "client_id"
}

    #data = "grant_type=client_credentials&client_id=string&client_secret=string&scope=string"
    payload_dict = json.dumps(data)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    print(payload_dict)
    try:
        print(colored("''''''''''REQUEST'''''''''''''''''","blue"))
        print(colored(f"Request: to {url}","blue"))
        print(colored(f"Request Headers: {headers}", "blue"))
        print(colored(f"''''''''''REQUEST'''''''''''''''''", "blue"))

        response = requests.post(url, headers=headers, data=data, cert=('dummy.crt', 'private.key'), verify='ca.crt')
        print(response.request.body)
        response.raise_for_status()
        response_payload = json.loads(response.text)

        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))
        print(colored(f"Response to: {response.url}","green"))
        print(colored(f"Response Headers: {response.headers}","green"))
        print(colored(f"Response: {response.json()}","green"))
        print(colored(f"Response Status code: {response.status_code}","green"))
        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))

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
            print("HOLA")
            invokerID = r.get('invokerID')
            capif_access_token = r.get('capif_access_token')
            ccf_discover_url = r.get('ccf_discover_url')
            #security_information = register_security_service(capif_ip, invokerID, capif_access_token, ccf_discover_url)
            #print(colored(json.dumps(security_information, indent=2),"yellow"))

            token = get_security_token(capif_ip, invokerID, capif_access_token, ccf_discover_url)
            print(colored(json.dumps(token, indent=2),"yellow"))
            #security_inf = get_security_service(capif_ip, invokerID, capif_access_token, ccf_discover_url)
            #print(security_inf)
            # getAEF_profiles = discovered_apis[0]["aef_profiles"][0]
            # getAEF_interfaces = getAEF_profiles["interface_descriptions"][0]
            # getAEF_versions = getAEF_profiles["versions"][0]
            # getAEF_resources = getAEF_versions["resources"][0]
            # r.set('demo_ipv4_addr', getAEF_interfaces["ipv4_addr"])
            # r.set('demo_port',  getAEF_interfaces["port"])
            # r.set('demo_url', getAEF_resources['uri'])

            print(colored("Discovered APIs","yellow"))

    except Exception as e:
        status_code = e.args[0]
        if status_code == 401:
            print("API Invoker is not authorized")
        elif status_code == 403:
            print("API Invoker does not exist. API Invoker id not found")
        else:
            print(e)