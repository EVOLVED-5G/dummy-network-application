# dummy-netapp

## Architecture

| Container             | Folder                | Description                                      |
|-----------------------|-----------------------|--------------------------------------------------|
| python_netapp         | pythonnetapp          | Python NetApp (communication example with CAPIF) |
| redis_netapp          | -                     | DB to store info exchanged with CAPIF            |
| nef_callback_server   | nef_callback_server   | Server implementing NEF callback endpoints       |
| capif_callback_netapp | capif_callback_netapp | Server implementing CAPIF callback endpoints     |

## Development status
| Development Task                    | Subtask                   | Status |
|-------------------------------------|---------------------------|--------|
| Communication with NEF (v. 1.4.0)   | Monitoring Event API      | ✅      |
|                                     | Session With QoS API      | ✅      |
|                                     | Connection Monitoring API | ✅      |
| Communication with CAPIF            | Register                  | ✅      |
|                                     | Invoker Management API    | ✅      |
|                                     | Discover Service API      | ✅      |
| Communication with dummy_aef        | -                         | ✅      |
| Use of NEF SDK libraries            | -                         | ✅      |
| Use of CAPIF SDK libraries          | -                         | ✅      |
| Callback server for NEF responses   | -                         | ✅      |
| Callback server for CAPIF responses | -                         | ✅      |
| TLS Communication with CAPIF        | -                         | ✅      |
| TLS Communication with NEF          | -                         | ❌      |


## Container management
Pre-condition:
- Deploy CAPIF and NEF stack (locally or on another server)

All configuration of the netapp is defined as environment variables 
in docker-compose.yml

If CAPIF and NEF are running on the same host as dummy_netapp,
then leave the configuration as it is. 
Otherwise, according to the architecture followed edit the variables:
- NEF_IP (setting it as the IP / server name of the host that NEF is deployed)
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
# Test NetApp with CAPIF and dummy_aef
python3 1_netapp_to_nef.py
python3 3_netapp_check_auth.py
python3 4_netapp_to_service.py

# Outside container, for clean-up
sudo rm ./pythonnetapp/*.crt ./pythonnetapp/*.key ./pythonnetapp/*.csr
```