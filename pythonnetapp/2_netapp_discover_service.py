import requests
import json
import configparser
import redis
import os
from termcolor import colored
from evolved5g.sdk import ServiceDiscoverer


if __name__ == '__main__':
    service_discoverer = ServiceDiscoverer(
        folder_path_for_certificates_and_api_key="/usr/src/app/capif_onboarding",
        capif_host="capifcore",
        capif_https_port=443
        )
    endpoints = service_discoverer.discover_service_apis()
    print(colored(f"Response: {json.dumps(endpoints, indent=2)}", "green"))