#!/bin/bash

docker-compose down --rmi all --remove-orphans || true

sudo rm ./pythonnetapp/*.crt ./pythonnetapp/*.key ./pythonnetapp/*.csr
