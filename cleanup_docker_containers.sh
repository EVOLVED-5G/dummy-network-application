#!/bin/bash

docker-compose down --rmi all --remove-orphans || true

sudo rm ./src/pythonnetapp/capif_onboarding/*
