#!/bin/bash

docker network create demo-network
docker-compose up --detach --remove-orphans --build
