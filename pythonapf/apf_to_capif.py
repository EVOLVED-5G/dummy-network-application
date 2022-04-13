import requests
import json
import configparser
import os
import redis

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

from OpenSSL.SSL import FILETYPE_PEM
from OpenSSL.crypto import (dump_certificate_request, dump_privatekey, load_publickey, PKey, TYPE_RSA, X509Req, dump_publickey)


def create_csr(csr_file_path):
    private_key_path = "private.key"

    # create public/private key
    key = PKey()
    key.generate_key(TYPE_RSA, 2048)

    # Generate CSR
    req = X509Req()
    req.get_subject().CN = 'apf'
    req.get_subject().O = 'Telefonica I+D'
    req.get_subject().OU = 'Innovation'
    req.get_subject().L = 'Madrid'
    req.get_subject().ST = 'Madrid'
    req.get_subject().C = 'ES'
    req.get_subject().emailAddress = 'inno@tid.es'
    req.set_pubkey(key)
    req.sign(key, 'sha256')

    with open(csr_file_path, 'wb+') as f:
        f.write(dump_certificate_request(FILETYPE_PEM, req))
        csr_request = dump_certificate_request(FILETYPE_PEM, req)
    with open(private_key_path, 'wb+') as f:
        f.write(dump_privatekey(FILETYPE_PEM, key))

    return csr_request


def register_apf_to_capif(capif_ip, capif_port, username, password, role, description, cn):
    url = "http://{}:{}/register".format(capif_ip, capif_port)

    payload = dict()
    payload['username'] = username
    payload['password'] = password
    payload['role'] = role
    payload['description'] = description
    payload['cn'] = cn

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_payload = json.loads(response.text)
        return response_payload['id'], response_payload['ccf_publish_url']
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


def publish_service_api_to_capif(capif_ip, jwt_token, ccf_url):

    csr_request = create_csr("cert_req.csr")

    url = 'http://{}:8080/sign-csr'.format(capif_ip)

    payload_dict = dict()
    payload_dict['csr'] = csr_request.decode("utf-8")
    payload_dict['mode'] = 'client'
    payload_dict['filename'] = 'apf'
    payload = json.dumps(payload_dict)

    headers = {
        'Content-Type': 'application/json'
    }

    certification_file = open('apf.crt', 'wb')
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        response_payload = json.loads(response.text)
        print(response_payload['certificate'])
        certification_file.write(bytes(response_payload['certificate'], 'utf-8'))
    except requests.exceptions.HTTPError as err:
        raise Exception(err.response.text, err.response.status_code)

    certification_file.close()

    url = 'https://{}/{}'.format(capif_ip, ccf_url)
    payload = open('service_api_description.json', 'rb')
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, cert=('apf.crt', 'private.key'), verify='ca.crt')
        response.raise_for_status()
        response_payload = json.loads(response.text)
        return response_payload['apiId']
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

    username = config.get("credentials", "apf_username")
    password = config.get("credentials", "apf_password")
    role = config.get("credentials", "apf_role")
    description = config.get("credentials", "apf_description")
    cn = config.get("credentials", "apf_cn")
    capif_ip = config.get("credentials", "capif_ip")
    capif_port = config.get("credentials", "capif_port")

    try:
        if not r.exists('apfID'):
            apfID, ccf_publish_url = register_apf_to_capif(capif_ip, capif_port, username, password, role, description,cn)
            r.set('apfID', apfID)
            r.set('ccf_publish_url', ccf_publish_url)
            print("APF ID: {}".format(apfID))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 409:
            print("User already registed. Continue with token request\n")
        else:
            print(e)

    try:
        if not r.exists('capif_access_token_apf'):
            capif_access_token = get_capif_token(capif_ip, capif_port, username, password, role)
            r.set('capif_access_token_apf', capif_access_token)
            print("Capif Token: {}".format(capif_access_token))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 401:
            print("Bad credentials. User not found\n")
        else:
            print(e)
        capif_access_token = None

    try:
        if r.exists('apfID'):
            # apfID = r.get('apfID')
            ccf_publish_url = r.get('ccf_publish_url')
            capif_access_token = r.get('capif_access_token_apf')
            service_api_id = publish_service_api_to_capif(capif_ip, capif_access_token, ccf_publish_url)
            if not r.exists('services_num'):
                services_num = 0
            else:
                services_num = int(r.get('services_num'))

            services_num += 1
            r.set('services_num', services_num)
            r.set('serviceapiid'+str(services_num), service_api_id)
            print("Service Api Id: {}".format(service_api_id))
    except Exception as e:
        status_code = e.args[1]
        if status_code == 401:
            message = e.args[0]
            if str(message).find("Token has expired") != -1:
                capif_access_token = get_capif_token(capif_ip, capif_port, username, password, role)
                r.set('capif_access_token_apf', capif_access_token)
                print("New Capif Token: {}".format(capif_access_token))
                print("Run the script again to publish a Service API")
            elif str(message).find("APF not existing") != -1:
                print("APF not existing. APF id not found")
            else:
                print(e)
        elif status_code == 403:
            print("Service already published.")
            print("Change API name and AEF Profile ID in service_api_description.json")
        else:
            print(e)