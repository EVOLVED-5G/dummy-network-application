#!/bin/bash

docker exec -it $(docker ps -q -f "name=redis") redis-cli