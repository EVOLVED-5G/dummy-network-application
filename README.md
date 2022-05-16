# dummy-netapp

## Architecture

| Container             | Folder                | Description                                      |
|-----------------------|-----------------------|--------------------------------------------------|
| python_netapp         | pythonnetapp          | Python NetApp (communication example with CAPIF) |
| python_apf            | pythonapf             | Python APF (communication example with CAPIF)    |
| redis                 | -                     | DB to store info exchanged with CAPIF            |
| web_netapp            | webnetapp             | HTML NetApp                                      |
| nef_callback_server   | nef_callback_server   | Server implementing NEF callback endpoints       |
| capif_callback_server | capif_callback_server | Server implementing CAPIF callback endpoints     |

## Development status
| Development Task                    | Subtask                | Status |
|-------------------------------------|------------------------|--------|
| Communication with NEF (v. 1.4.0)   | Monitoring Event API   | ✅      |
|                                     | Session With QoS API   | ✅      |
| Communication with CAPIF            | Register (Invoker/APF) | ✅      |
|                                     | Publish Service API    | ✅      |
|                                     | Invoker Management API | ✅      |
|                                     | Discover Service API   | ✅      |
| Use of NEF SDK libraries            | -                      | ✅      |
| Use of CAPIF SDK libraries          | -                      | ❌      |
| Callback server for NEF responses   | -                      | ✅      |
| Callback server for CAPIF responses | -                      | ✅      |
| TLS Communication with CAPIF        | -                      | ❌      |
| TLS Communication with NEF          | -                      | ❌      |


## Container management
Pre-condition:
- Deploy CAPIF and NEF stack (locally or on another server)
- Define IPs* and ports of CAPIF, NEF and callback server (in files credentails.properties)

*If CAPIF and NEF are running on the same host as dummy_netapp,
then leave the IP properties as "host.docker.internal". 
Otherwise, add the IP of their host (e.g. "192.168.X.X"). 

```shell
# Deploy and run containers
./run.sh

# Stop containers
./stop.sh

# Stop and Remove containers
./cleanup_docker_containers.sh
```

## Use Python APF
Pre-condition: Deploy CAPIF stack
```shell
# Access Python NetApp
./terminal_to_py_apf.sh

# Inside the container
python3 apf_to_capif.py

# Outside container, for clean-up
sudo rm ca.crt private.key cert_req.csr apf.crt
```

## Use Python NetApp

```shell
# Access Python NetApp
./terminal_to_py_netapp.sh

# Inside the container
python3 netapp_to_capif.py
python3 netapp_to_nef.py

# Outside container, for clean-up
sudo rm ca.crt private.key cert_req.csr dummy.crt
```