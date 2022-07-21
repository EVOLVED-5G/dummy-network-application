#!/bin/bash
HOSTNAME=capifcore
if [ "$#" -eq 1 ]; then
    HOSTNAME=$1
fi
echo Nginx hostname will be $HOSTNAME

CAPIF_HOSTNAME=$HOSTNAME docker-compose up --detach --remove-orphans --build
