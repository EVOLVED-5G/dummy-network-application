# dummy-netapp

## Architecture

| Container             | Folder                | Description                                      |
|-----------------------|-----------------------|--------------------------------------------------|
| python_netapp         | pythonnetapp          | Python NetApp (communication example with CAPIF) |
| redis_netapp          | -                     | DB to store info exchanged with CAPIF            |
| nef_callback_server   | nef_callback_server   | Server implementing NEF callback endpoints       |
| capif_callback_netapp | capif_callback_netapp | Server implementing CAPIF callback endpoints     |

## Development status
| Development Task                    | Subtask                | Status |
|-------------------------------------|------------------------|--------|
| Communication with NEF (v. 1.4.0)   | Monitoring Event API   | ✅      |
|                                     | Session With QoS API   | ✅      |
| Communication with CAPIF            | Register               | ✅      |
|                                     | Invoker Management API | ✅      |
|                                     | Discover Service API   | ✅      |
| Communication with dummy_aef        | -                      | ✅      |
| Use of NEF SDK libraries            | -                      | ✅      |
| Use of CAPIF SDK libraries          | -                      | ❌      |
| Callback server for NEF responses   | -                      | ✅      |
| Callback server for CAPIF responses | -                      | ✅      |
| TLS Communication with CAPIF        | -                      | ✅      |
| TLS Communication with NEF          | -                      | ❌      |


## Container management
Pre-condition:
- Deploy CAPIF, dummy_aef and NEF stack (locally or on another server)
- Define IPs* and ports of CAPIF, NEF and callback server (in files credentails.properties)

*If CAPIF and NEF are running on the same host as dummy_netapp,
then leave the IP properties as "host.docker.internal". 
Otherwise, add the IP of their host (e.g. "192.168.X.X"). 

**For communication with dummy_aef, demo-network is created.

```shell
# Deploy and run containers
./run.sh

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
python3 1_netapp_to_capif.py
python3 2_netapp_discover_service.py
python3 3_netapp_check_auth.py
python3 4_netapp_to_service.py
# Test NetApp with NEF Emulator
python3 netapp_to_nef.py

# Outside container, for clean-up
sudo rm ./pythonnetapp/*.crt ./pythonnetapp/*.key ./pythonnetapp/*.csr
```