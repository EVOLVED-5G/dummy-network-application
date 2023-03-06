# dummy-netapp

## Architecture

| Container             | Folder                | Description                                      |
|-----------------------|-----------------------|--------------------------------------------------|
| python_netapp         | pythonnetapp          | Python NetApp (communication example with CAPIF) |
| redis_netapp          | -                     | DB to store info exchanged with CAPIF            |
| nef_callback_server   | nef_callback_server   | Server implementing NEF callback endpoints       |
| capif_callback_netapp | capif_callback_netapp | Server implementing CAPIF callback endpoints     |

## Development status

| Development Task                    | Subtask                            | Status |
|-------------------------------------|------------------------------------|--------|
| Communication with CAPIF (v. 3.0)   | Register                           | ✅      |
|                                     | Invoker Management API             | ✅      |
|                                     | Discover Service API               | ✅      |
|                                     | Security API                       | ✅      |
| Communication with NEF (v. 2.0.0)   | Monitoring Event API               | ✅      |
|                                     | Session With QoS API               | ✅      |
|                                     | Connection Monitoring API          | ✅      |
| Communication with TSN              | [GET] /profile API                 | ✅      |
|                                     | [GET] /profile?name=<profile_name> | ✅      |
|                                     | [POST] /apply                      | ✅      |
|                                     | [POST] /clear                      | ✅      |
| Use of CAPIF SDK libraries          | -                                  | ✅      |
| Use of NEF SDK libraries            | -                                  | ✅      |
| Use of TSN SDK libraries            | -                                  | ✅      |
| TLS Communication with CAPIF        | -                                  | ✅      |
| TLS Communication with NEF          | -                                  | ✅      |
| TLS Communication with TSN          | -                                  | ❌      |
| Callback server for NEF responses   | -                                  | ✅      |
| Callback server for CAPIF responses | -                                  | ✅      |
| Callback server for TSN responses   | -                                  | ❌      |
| Communication with dummy_aef        | -                                  | ✅      |


## Container management
Pre-condition:
- Deploy CAPIF, NEF and TSN stack (locally or on another server)

All configuration of the netapp is defined as environment variables 
in docker-compose.yml

If CAPIF, NEF and TSN are running on the same host as dummy_netapp,
then leave the configuration as it is. 
Otherwise, according to the architecture followed edit the variables:
- NEF_IP and TSN_IP (setting it as the IP / server name of the host that NEF is deployed)
- NEF_CALLBACK_IP & CAPIF_CALLBACK_URL (setting them as the IP / server name of the host that dummy netapp is deployed)

**For communication with dummy_aef, demo-network is created.

```shell
# Deploy and run containers
./run.sh

# Access Redis cli (to see NEF access token, responses and callbacks)
./redis_cli.sh

## Inside redis cli, execute the following command 
## to see the redis variables where the info is stored
keys *

## Inside redis cli, execute the following command 
## to see the content of a redis variable
get *key*


# Stop containers
./stop.sh

# Stop and Remove containers
./cleanup_docker_containers.sh
```

## Use Python NetApp

```shell
# Access Python NetApp
./terminal_to_py_netapp.sh

# Inside the container
# Test NetApp with CAPIF and NEF
python3 0_netapp_to_nef.py

# Test NetApp with CAPIF and TSN
python3 0_netapp_to_tsn.py

# Test NetApp with CAPIF and dummy_aef
# IMPORTANT: to test with dummy_aef, do not deploy NEF or/and TSN. It must be tested on its own
python3 1_netapp_to_capif.py
python3 2_netapp_to_events.py
python3 3_netapp_discover_service.py
python3 4_netapp_to_security.py
#In dummy_aef execute 5_aef_service_oauth.py
python3 5_netapp_to_service_oauth.py
#In dummy_aef execute 6_aef_security.py
python3 6_netapp_check_auth_pki.py
#In dummy_aef execute 7_aef_service_pki.py
python3 7_netapp_to_service_pki.py

# Outside container, for clean-up
(
sudo rm ./pythonnetapp/capif_onboarding/*
sudo rm ./pythonnetapp/demo_values.json 
sudo rm ./pythonnetapp/ca.crt 
sudo rm ./pythonnetapp/cert_req.csr 
sudo rm ./pythonnetapp/dummy.crt 
sudo rm ./pythonnetapp/private.key 
sudo rm ./pythonnetapp/ca_service.crt
)
```