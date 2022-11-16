import redis
import os
import datetime

from evolved5g.sdk import LocationSubscriber, QosAwareness, ConnectionMonitor
from evolved5g.swagger_client import UsageThreshold, Configuration, ApiClient, LoginApi

# Get environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def request_nef_token(nef_host):
    configuration = Configuration()
    configuration.host = nef_host
    api_client = ApiClient(configuration=configuration)
    api_client.select_header_content_type(["application/x-www-form-urlencoded"])
    api = LoginApi(api_client)
    token = api.login_access_token_api_v1_login_access_token_post("", nef_user, nef_pass, "", "", "")

    return token


def monitor_subscription(times, host, access_token, certificate_folder, capifhost, capifport, callback_server):
    expire_time = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    netapp_id = "myNetapp"
    location_subscriber = LocationSubscriber(host, access_token, certificate_folder, capifhost, capifport)
    external_id = "10001@domain.com"

    subscription = location_subscriber.create_subscription(
        netapp_id=netapp_id,
        external_id=external_id,
        notification_destination=callback_server,
        maximum_number_of_reports=times,
        monitor_expire_time=expire_time
    )
    monitoring_response = subscription.to_dict()

    return monitoring_response


def connection_monitoring(host, access_token, certificate_folder, capifhost, capifport, callback_server):
    expire_time = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z"
    netapp_id = "myNetapp"
    connection_monitor = ConnectionMonitor(host, access_token, certificate_folder, capifhost, capifport)
    external_id = "10001@domain.com"

    subscription_when_not_connected = connection_monitor.create_subscription(
        netapp_id=netapp_id,
        external_id=external_id,
        notification_destination=callback_server,
        monitoring_type=ConnectionMonitor.MonitoringType.INFORM_WHEN_CONNECTED,
        wait_time_before_sending_notification_in_seconds=5,
        maximum_number_of_reports=1000,
        monitor_expire_time=expire_time
    )
    connection_monitoring_response = subscription_when_not_connected.to_dict()

    return connection_monitoring_response

def sessionqos_subscription(host, access_token, certificate_folder, capifhost, capifport, callback_server):
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

    subscription = qos_awereness.create_guaranteed_bit_rate_subscription(
        netapp_id=netapp_id,
        equipment_network_identifier=equipment_network_identifier,
        network_identifier=network_identifier,
        notification_destination=callback_server,
        gbr_qos_reference=conversational_voice,
        usage_threshold=usage_threshold,
        qos_monitoring_parameter=uplink,
        threshold=uplink_threshold,
        reporting_mode=QosAwareness.EventTriggeredReportingConfiguration(wait_time_in_seconds=10)
    )

    qos_awereness_response = subscription.to_dict()

    return qos_awereness_response


if __name__ == '__main__':

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )

    nef_url = "http://{}:{}".format(os.getenv('NEF_IP'), os.environ.get('NEF_PORT'))
    nef_callback = "http://{}:{}/nefcallbacks".format(os.getenv('NEF_CALLBACK_IP'), os.environ.get('NEF_CALLBACK_PORT'))
    nef_user = os.getenv('NEF_USER')
    nef_pass = os.environ.get('NEF_PASS')
    capif_host = os.getenv('CAPIF_HOSTNAME')
    capif_https_port = os.environ.get('CAPIF_PORT_HTTPS')
    folder_path_for_certificates_and_capif_api_key = os.environ.get('PATH_TO_CERTS')

    try:
        if not r.exists('nef_access_token'):
            token = request_nef_token(nef_url)
            r.set('nef_access_token', token.access_token)
            print("NEF Token: {}\n".format(token.access_token))
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test Monitoring Event API? (Y/n) ")
        if ans == "Y" or ans == 'y':
            times = input("Number of location monitoring callbacks: ")
            last_response_from_nef = monitor_subscription(int(times),
                                                          nef_url,
                                                          nef_access_token,
                                                          folder_path_for_certificates_and_capif_api_key,
                                                          capif_host, capif_https_port, nef_callback)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test Connection Monitoring API? (Y/n) ")
        if ans == "Y" or ans == 'y':
            last_response_from_nef = connection_monitoring(nef_url,
                                                          nef_access_token,
                                                          folder_path_for_certificates_and_capif_api_key,
                                                          capif_host, capif_https_port, nef_callback)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
            print("\n---- IMPORTANT ----")
            print(
                "To delete Connection monitoring subscription, execute the following command (outside of the container, from a host that can see NEF IP and 'curl' is installed):\n")
            sub_resource = last_response_from_nef['link']
            sub_resource_final = sub_resource.replace('host.docker.internal', 'localhost')
            print("curl --request DELETE {} --header 'Authorization: Bearer {}'".format(sub_resource_final, nef_access_token))
            print("\n-------------------\n")
    except Exception as e:
        status_code = e.args[1]
        print(e)

    try:
        nef_access_token = r.get('nef_access_token')
        ans = input("Do you want to test Session-with-QoS API? (Y/n) ")
        if ans == "Y" or ans == 'y':
            last_response_from_nef = sessionqos_subscription(nef_url,
                                                             nef_access_token,
                                                             folder_path_for_certificates_and_capif_api_key,
                                                             capif_host, capif_https_port, nef_callback)
            r.set('last_response_from_nef', str(last_response_from_nef))
            print("{}\n".format(last_response_from_nef))
            print("\n---- IMPORTANT ----")
            print(
                "To delete QoS subscription, execute the following command (outside of the container, from a host that can see NEF IP and 'curl' is installed):\n")
            sub_resource = last_response_from_nef['link']
            sub_resource_final = sub_resource.replace('host.docker.internal', 'localhost')
            print("curl --request DELETE {} --header 'Authorization: Bearer {}'".format(sub_resource_final, nef_access_token))
            print("\n-------------------\n")
    except Exception as e:
        status_code = e.args[1]
        print(e)
