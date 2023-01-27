#!/bin/bash

docker-compose down --rmi all --remove-orphans || true

sudo rm ./pythonnetapp/capif_onboarding/*

# sudo rm ./pythonnetapp/demo_values.json && sudo rm ./pythonnetapp/ca.crt && sudo rm ./pythonnetapp/cert_req.csr && sudo rm ./pythonnetapp/dummy.crt && sudo rm ./pythonnetapp/private.key && sudo rm ./pythonnetapp/ca_service.crt

# sudo rm ./pythonnetapp/demo_values.json
# sudo rm ./pythonnetapp/ca.crt
# sudo rm ./pythonnetapp/cert_req.csr
# sudo rm ./pythonnetapp/dummy.crt
# sudo rm ./pythonnetapp/private.key