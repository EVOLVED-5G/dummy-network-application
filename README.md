# dummy-netapp

## Architecture

| Container       | Folder          | Description                                      |
|-----------------|-----------------|--------------------------------------------------|
| python_netapp   | pythonnetapp    | Python NetApp (communication example with CAPIF) |
| redis           | -               | DB to store info exchanged with CAPIF            |
| web_netapp      | webnetapp       | HTML NetApp                                      |
| callback_server | callback_server | Server implementing NEF callback endpoints       |


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

## Use Python NetApp
Pre-condition: Deploy CAPIF stack
```shell
# Access Python NetApp
./terminal_to_py_netapp.sh

# Inside the container
python3 apf_to_capif.py
python3 netapp_to_capif.py
python3 netapp_to_nef.py
```