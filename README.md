# dummy-netapp

## Architecture

| Container     | Folder       | Description                                      |
|---------------|--------------|--------------------------------------------------|
| python_netapp | pythonnetapp | Python NetApp (communication example with CAPIF) |
| redis         | -            | DB to store info exchanged with CAPIF            |
| web_netapp    | webnetapp    | HTML NetApp                                      |


## Container management
Pre-condition: Deploy CAPIF stack
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
```