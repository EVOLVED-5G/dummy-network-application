from dis import dis
import requests
import json
import configparser
import redis
import os
from termcolor import colored

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def check_auth_to_aef(capif_ip, path, crt):

    print(colored("Going to check auth to AEF","yellow"))

    #url = "https://python_aef:8085/check-authentication"
    url = "https://{}:443/check-authentication".format(capif_ip)
    print(url)

    crt_path_file = path + crt
    # print(crt_path_file)
    prkey_path_file = path + "private.key"
    # print(prkey_path_file)

    payload = {
        "apiInvokerId": "",
        "supportedFeatures": ""

    }

    files = {}
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        print(colored("''''''''''REQUEST'''''''''''''''''","blue"))
        print(colored(f"Request: to {url}","blue"))
        print(colored(f"Request Headers: {headers}", "blue"))
        print(colored(f"''''''''''REQUEST'''''''''''''''''", "blue"))
        response = requests.request("POST", url, headers=headers, data=payload, files=files, cert=(crt_path_file, prkey_path_file), verify=False)
        response.raise_for_status()
        response_payload = json.loads(response.text)
        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))
        print(colored(f"Response to: {response.url}","green"))
        print(colored(f"Response Headers: {response.headers}","green"))
        print(colored(f"Response: {response.json()}","green"))
        print(colored(f"Response Status code: {response.status_code}","green"))
        print(colored("Success to obtain auth of AEF","green"))
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

    capif_ip = os.getenv('CAPIF_HOSTNAME')
    capif_port = os.getenv('CAPIF_PORT')

    f = open('./capif_onboarding/capif_api_details.json')
    data = json.load(f)

    try:
        if data['api_invoker_id']:

            invokerID = data['api_invoker_id']
            ccf_discover_url = data['discover_services_url']
            path_to_files = "./capif_onboarding/"
            crt_file = data['csr_common_name'] + ".crt"

            demo_ip = r.get('demo_ipv4_addr')
            discovered_apis = check_auth_to_aef(demo_ip, path_to_files, crt_file)
            r.set("jwt_token", discovered_apis["access_token"])
            print(colored("Invoker Authrized to use AEF","yellow"))
            print(colored(json.dumps(discovered_apis, indent=2),"yellow"))

    except Exception as e:
        status_code = e.args[0]
        if status_code == 401:
            print("API Invoker is not authorized")
        elif status_code == 403:
            print("API Invoker does not exist. API Invoker id not found")
        else:
            print(e)