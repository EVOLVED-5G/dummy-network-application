import requests
import json
import configparser
import redis
import os
import datetime
import re

from evolved5g.sdk import LocationSubscriber, QosAwareness
from evolved5g import swagger_client
from evolved5g.swagger_client import LoginApi, UsageThreshold
from evolved5g.swagger_client.models import Token
import emulator_utils

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def register_netapp_to_nef(nef_ip, nef_port) -> Token:
    configuration = swagger_client.Configuration()
    # The host of the 5G API (emulator)
    configuration.host = "http://{}:{}".format(nef_ip, nef_port)
    api_client = swagger_client.ApiClient(configuration=configuration)
    api_client.select_header_content_type(["application/x-www-form-urlencoded"])
    api = LoginApi(api_client)
    nef_user = "admin@my-email.com"
    nef_pass = "pass"
    token = api.login_access_token_api_v1_login_access_token_post("", nef_user, nef_pass, "", "", "")

    return token


def monitor_subscription(times, host, access_token, certificate_folder, capifhost, capifport):
    expire_time = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    netapp_id = "myNetapp"
    location_subscriber = LocationSubscriber(host, access_token, certificate_folder, capifhost, capifport)
    external_id = "10001@domain.com"
    callback_host = emulator_utils.get_callback_server_for_nef_responses()

    subscription = location_subscriber.create_subscription(
        netapp_id=netapp_id,
        external_id=external_id,
        notification_destination=callback_host,
        maximum_number_of_reports=times,
        monitor_expire_time=expire_time
    )
    monitoring_response = subscription.to_dict()

    return monitoring_response


def sessionqos_subscription(host, access_token, certificate_folder, capifhost, capifport):
    netapp_id = "myNetapp"
    qos_awereness = QosAwareness(host, access_token, certificate_folder, capifhost, capifport)
    equipment_network_identifier = "10.0.0.1"
    network_identifier = QosAwareness.NetworkIdentifier.IP_V4_ADDRESS
    conversational_voice = QosAwareness.GBRQosReference.CONVERSATIONAL_VOICE
    # In this scenario we monitor UPLINK
    uplink = QosAwareness.QosMonitoringParameter.UPLINK
    # Minimum delay of data package during uplink, in milliseconds
    uplink_threshold = 20
    gigabyte = 1024 * 1024 * 1024
    # Up to 10 gigabytes 5 GB downlink, 5gb uplink
    usage_threshold = UsageThreshold(duration=None,  # not supported
                                     total_volume=10 * gigabyte,  # 10 Gigabytes of total volume
                                     downlink_volume=5 * gigabyte,  # 5 Gigabytes for downlink
                                     uplink_volume=5 * gigabyte  # 5 Gigabytes for uplink
                                     )
    notification_destination = emulator_utils.get_callback_server_for_nef_responses()

    subscription = qos_awereness.create_guaranteed_bit_rate_subscription(
        netapp_id=netapp_id,
        equipment_network_identifier=equipment_network_identifier,
        network_identifier=network_identifier,
        notification_destination=notification_destination,
        gbr_qos_reference=conversational_voice,
        usage_threshold=usage_threshold,
        qos_monitoring_parameter=uplink,
        threshold=uplink_threshold,
        wait_time_between_reports=10
    )

    qos_awereness_response = subscription.to_dict()

    return qos_awereness_response


def qos_characteristics(access_token):
    host = emulator_utils.get_host_of_the_nef_emulator()
    url = "{}/api/v1/qosInfo/qosCharacteristics".format(host)

    headers = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + access_token
    }

    response = requests.request('GET', url, headers=headers)
    parsed = json.loads(response.text)

    return parsed


def qos_profiles(access_token):
    host = emulator_utils.get_host_of_the_nef_emulator()
    url = "{}/api/v1/qosInfo/qosProfiles/AAAAA1".format(host)

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

    try:
        if not r.exists('nef_access_token'):
            nef_access_token = emulator_utils.get_token()
            r.set('nef_access_token', nef_access_token.access_token)
            print("NEF Token: {}\n".format(nef_access_token.access_token))
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test Monitoring Event API? (Y/n) ")
        nef_url = emulator_utils.get_host_of_the_nef_emulator()
        folder_path_for_certificates_and_capif_api_key = "/usr/src/app/capif_onboarding"
        capif_host = "capifcore"
        capif_https_port = 443
        if ans == "Y" or ans == 'y':
            times = input("Number of location monitoring callbacks: ")
            last_response_from_nef = monitor_subscription(int(times),
                                                          nef_url,
                                                          nef_access_token,
                                                          folder_path_for_certificates_and_capif_api_key,
                                                          capif_host, capif_https_port)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test Session-with-QoS API? (Y/n) ")
        nef_url = emulator_utils.get_url_of_the_nef_emulator()
        folder_path_for_certificates_and_capif_api_key = "/usr/src/app/capif_onboarding"
        capif_host = "capifcore"
        capif_https_port = 443
        if ans == "Y" or ans == 'y':
            last_response_from_nef = sessionqos_subscription(nef_url,
                                                             nef_access_token,
                                                             folder_path_for_certificates_and_capif_api_key,
                                                             capif_host, capif_https_port)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
            print("\n---- IMPORTANT ----")
            print(
                "To delete QoS subscription, execute the following command (from a host that can see NEF IP and 'curl' is installed):\n")
            sub_resource = last_response_from_nef['link']
            print("curl --request DELETE {} --header 'Authorization: Bearer {}'".format(sub_resource, nef_access_token))
            print("\n-------------------\n")
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test QoS Information APIs? (Y/n) ")
        if ans == "Y" or ans == 'y':
            last_response_from_nef = qos_characteristics(nef_access_token)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
            last_response_from_nef = qos_profiles(nef_access_token)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
    except Exception as e:
        status_code = e.args[1]
        print(e)
