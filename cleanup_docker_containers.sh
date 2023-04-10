#!/bin/bash

docker-compose down --rmi all --remove-orphans || true

(
sudo rm ./src/pythonnetapp/capif_onboarding/*
sudo rm ./src/pythonnetapp/demo_values.json
sudo rm ./src/pythonnetapp/ca.crt
sudo rm ./src/pythonnetapp/cert_req.csr
sudo rm ./src/pythonnetapp/dummy.crt
sudo rm ./src/pythonnetapp/private.key
sudo rm ./src/pythonnetapp/ca_service.crt
)

# sudo rm ./pythonnetapp/demo_values.json && sudo rm ./pythonnetapp/ca.crt && sudo rm ./pythonnetapp/cert_req.csr && sudo rm ./pythonnetapp/dummy.crt && sudo rm ./pythonnetapp/private.key && sudo rm ./pythonnetapp/ca_service.crt

# sudo rm ./pythonnetapp/demo_values.json
# sudo rm ./pythonnetapp/ca.crt
# sudo rm ./pythonnetapp/cert_req.csr
# sudo rm ./pythonnetapp/dummy.crt
# sudo rm ./pythonnetapp/private.key