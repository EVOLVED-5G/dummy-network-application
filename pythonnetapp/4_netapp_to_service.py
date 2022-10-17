from dis import dis
import requests
import json
import configparser
import redis
import os
import argparse
from termcolor import colored

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def demo_to_aef(demo_ip, demo_port, demo_url, jwt_token, name):

    print(colored("Using AEF Service API","yellow"))
    url = "http://{}:{}{}".format(demo_ip, demo_port, demo_url)
    #url = "http://python_aef:8086/hello"

    payload = json.dumps({
        "name": name
    })

    files = {}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+jwt_token
    }

    try:
        print(colored("''''''''''REQUEST'''''''''''''''''","blue"))
        print(colored(f"Request: to {url}","blue"))
        print(colored(f"Request Headers: {headers}", "blue"))
        print(colored(f"Request Body: {json.dumps(payload)}", "blue"))
        print(colored(f"''''''''''REQUEST'''''''''''''''''", "blue"))
        response = requests.request("POST", url, headers=headers, data=payload, files=files, cert=('dummy.crt', 'private.key'), verify=False)
        response.raise_for_status()
        response_payload = json.loads(response.text)
        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))
        print(colored(f"Response to: {response.url}","green"))
        print(colored(f"Response Headers: {response.headers}","green"))
        print(colored(f"Response: {response.json()}","green"))
        print(colored(f"Response Status code: {response.status_code}","green"))
        print(colored("Success to invoke service","green"))
        print(colored(response_payload,"green"))
        print(colored("''''''''''RESPONSE'''''''''''''''''","green"))
        return response_payload
    except requests.exceptions.HTTPError as err:
        print(err.response.text)
        message = json.loads(err.response.text)
        status = err.response.status_code
        raise Exception(message, status)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', metavar= "name", type=str, default="Evolve5G", help="Name to send to the aef service")
    args = parser.parse_args()
    input_name = args.name

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
        if r.exists('jwt_token'):

            print(colored("Doing test","yellow"))
            jwt_token = r.get('jwt_token')
            invokerID = r.get('invokerID')
            capif_access_token = r.get('capif_access_token')
            demo_ip = r.get('demo_ipv4_addr')
            demo_port = r.get('demo_port')
            demo_url = r.get('demo_url')
            result = demo_to_aef(demo_ip, demo_port, demo_url, jwt_token, input_name)
            print(colored("Success","yellow"))
    except Exception as e:
        status_code = e.args[0]
        if status_code == 401:
            print("API Invoker is not authorized")
        elif status_code == 403:
            print("API Invoker does not exist. API Invoker id not found")
        else:
            print(e)