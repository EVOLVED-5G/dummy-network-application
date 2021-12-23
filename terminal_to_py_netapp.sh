#!/bin/bash

docker exec -it $(docker ps -q -f "name=python_netapp") bash