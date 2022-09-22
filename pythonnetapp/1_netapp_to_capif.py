from dis import dis
import requests
import json
import configparser
import redis
import os

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
    req.get_subject().CN = config.get("credentials", "invoker_cn")
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


def register_netapp_to_capif(capif_ip, capif_port, username, password, role, description, cn):

    print("Registering API Invoker to CAPIF")
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
        print("''''''''''REQUEST'''''''''''''''''")
        print("Request: to ",url) 
        print("Request Headers: ",  headers) 
        print("Request Body: ", json.dumps(payload))
        print("''''''''''REQUEST'''''''''''''''''")

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_payload = json.loads(response.text)
        print("''''''''''RESPONSE'''''''''''''''''")
        print("Response to: ",response.url) 
        print("Response Headers: ",  response.headers) 
        print("Response: ", response.json())
        print("Response Status code: ", response.status_code)
        print("Invoker registered successfuly")
        print("''''''''''RESPONSE'''''''''''''''''")
        return response_payload['id'], response_payload['ccf_onboarding_url'], response_payload['ccf_discover_url'],
    except requests.exceptions.HTTPError as err:
        raise Exception(err.response.text, err.response.status_code)


def get_capif_token(capif_ip, capif_port, username, password, role):

    print("Invoker Get CAPIF auth")
    url = "http://{}:{}/getauth".format(capif_ip, capif_port)

    payload = dict()
    payload['username'] = username
    payload['password'] = password
    payload['role'] = role

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        print("''''''''''REQUEST'''''''''''''''''")
        print("Request: to ",url) 
        print("Request Headers: ",  headers) 
        print("Request Body: ", json.dumps(payload))
        print("''''''''''REQUEST'''''''''''''''''")

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_payload = json.loads(response.text)

        print("''''''''''RESPONSE'''''''''''''''''")
        print("Response to: ",response.url) 
        print("Response Headers: ",  response.headers) 
        print("Response: ", response.json())
        print("Response Status code: ", response.status_code)
        print("Access Token obtained")
        print("''''''''''RESPONSE'''''''''''''''''")
    
        ca_root_file = open('ca.crt', 'wb+')
        ca_root_file.write(bytes(response_payload['ca_root'], 'utf-8'))
        return response_payload['access_token']
    except requests.exceptions.HTTPError as err:
        raise Exception(err.response.text, err.response.status_code)


def onboard_netapp_to_capif(capif_ip, capif_callback_ip, capif_callback_port, jwt_token, ccf_url):

    print("Onboarding netapp to CAPIF")
    url = 'https://{}/{}'.format(capif_ip, ccf_url)

    csr_request = create_csr("cert_req.csr")

    json_file = open('invoker_details.json', 'rb')
    payload_dict = json.load(json_file)
    payload_dict['onboardingInformation']['apiInvokerPublicKey'] = csr_request.decode("utf-8")
    payload_dict['notificationDestination'] = payload_dict['notificationDestination'].replace("X", capif_callback_ip)
    payload_dict['notificationDestination'] = payload_dict['notificationDestination'].replace("Y", capif_callback_port)
    payload = json.dumps(payload_dict)

    headers = {
        'Authorization': 'Bearer {}'.format(jwt_token),
        'Content-Type': 'application/json'
    }

    try:
        print("''''''''''REQUEST'''''''''''''''''")
        print("Request: to ",url) 
        print("Request Headers: ",  headers) 
        print("Request Body: ", json.dumps(payload))
        print("''''''''''REQUEST'''''''''''''''''")

        response = requests.request("POST", url, headers=headers, data=payload, verify='ca.crt')
        response.raise_for_status()
        response_payload = json.loads(response.text)
        certification_file = open('dummy.crt', 'wb')
        certification_file.write(bytes(response_payload['onboardingInformation']['apiInvokerCertificate'], 'utf-8'))
        certification_file.close()

        print("''''''''''RESPONSE'''''''''''''''''")
        print("Response to: ",response.url) 
        print("Response Headers: ",  response.headers) 
        print("Response: ", response.json())
        print("Response Status code: ", response.status_code)
        print("Success onboard invoker")
        print("''''''''''RESPONSE'''''''''''''''''")
        return response_payload['apiInvokerId']
    except requests.exceptions.HTTPError as err:
        raise Exception(err.response.text, err.response.status_code)





if __name__ == '__main__':

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )

    #Remove data from Redis
    keys = r.keys('*')
    if len(keys) != 0:
        r.delete(*keys)


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
        if not r.exists('netappID'):
            netappID, ccf_onboarding_url, ccf_discover_url = register_netapp_to_capif(capif_ip, capif_port, username, password, role, description, cn)
            r.set('netappID', netappID)
            r.set('ccf_onboarding_url', ccf_onboarding_url)
            r.set('ccf_discover_url', ccf_discover_url)
            print("NetAppID: {}\n".format(netappID))
    except Exception as e:
        status_code = e.args[0]
        if status_code == 409:
            print("User already registed. Continue with token request\n")
        else:
            print(e)

    try:
        capif_access_token = get_capif_token(capif_ip, capif_port, username, password, role)
        r.set('capif_access_token', capif_access_token)
        print("Capif Token: {}\n".format(capif_access_token))
    except Exception as e:
        status_code = e.args[0]
        if status_code == 401:
            print("Bad credentials. User not found\n")
        else:
            print(e)
        capif_access_token = None

    try:
        if not r.exists('invokerID'):
            capif_access_token = r.get('capif_access_token')
            ccf_onboarding_url = r.get('ccf_onboarding_url')
            invokerID = onboard_netapp_to_capif(capif_ip, capif_callback_ip, capif_callback_port, capif_access_token, ccf_onboarding_url)
            r.set('invokerID', invokerID)
            print("ApiInvokerID: {}\n".format(invokerID))
    except Exception as e:
        status_code = e.args[0]
        if status_code == 401:
            capif_access_token = get_capif_token(capif_ip, capif_port, username, password, role)
            r.set('capif_access_token', capif_access_token)
            ccf_onboarding_url = r.get('ccf_onboarding_url')
            print("New Capif Token: {}\n".format(capif_access_token))
            invokerID = onboard_netapp_to_capif(capif_ip, capif_callback_ip, capif_callback_port, capif_access_token, ccf_onboarding_url)
            data_invoker = [{"invokerID": invokerID}]
            r.set('invokerID', invokerID)
            print("ApiInvokerID: {}\n".format(invokerID))
        elif status_code == 403:
            print("Invoker already registered.")
            print("Chanage invoker public key in invoker_details.json\n")
        else:
            print(e)

