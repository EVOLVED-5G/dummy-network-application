from evolved5g import swagger_client
from evolved5g.swagger_client import LoginApi, User
from evolved5g.swagger_client.models import Token
import configparser


def get_token() -> Token:

    username = "admin@my-email.com"
    password = "pass"
    # User name and pass matches are set in the .env of the docker of NEF_EMULATOR. See
    # https://github.com/EVOLVED-5G/NEF_emulator
    configuration = swagger_client.Configuration()
    # The host of the 5G API (emulator)
    configuration.host = get_host_of_the_nef_emulator()
    api_client = swagger_client.ApiClient(configuration=configuration)
    api_client.select_header_content_type(["application/x-www-form-urlencoded"])
    api = LoginApi(api_client)
    token = api.login_access_token_api_v1_login_access_token_post("", username, password, "", "", "")
    return token


def get_api_client(token) -> swagger_client.ApiClient:
    configuration = swagger_client.Configuration()
    configuration.host = get_host_of_the_nef_emulator()
    configuration.access_token = token.access_token
    api_client = swagger_client.ApiClient(configuration=configuration)
    return api_client


def get_host_of_the_nef_emulator() -> str:
    config = configparser.ConfigParser()
    config.read('credentials.properties')

    nef_ip = config.get("credentials", "nef_ip")
    nef_port = config.get("credentials", "nef_port")
    return "http://{}:{}".format(nef_ip, nef_port)


def get_callback_server_for_nef_responses() -> str:
    config = configparser.ConfigParser()
    config.read('credentials.properties')

    callback_ip = config.get("credentials", "nef_callback_ip")
    callback_port = config.get("credentials", "nef_callback_port")
    return "http://{}:{}/nefcallbacks".format(callback_ip, callback_port)