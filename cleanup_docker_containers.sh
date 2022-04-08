#!/bin/bash

docker-compose down --rmi all --remove-orphans || true
#cd pythonnetapp/
#sudo rm ca.crt private.key solicitud.csr dummy.crt