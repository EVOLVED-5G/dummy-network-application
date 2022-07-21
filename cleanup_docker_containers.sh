#!/bin/bash

docker-compose down --rmi all --remove-orphans || true

#cd pythonnetapp && sudo rm ca.crt private.key cert_req.csr dummy.crt && cd ..
#cd pythonexposer && sudo rm ca.crt private.key cert_req.csr exposer.crt && cd ..