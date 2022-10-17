#!/bin/bash

docker-compose down --rmi all --remove-orphans || true

sudo rm ./pythonnetapp/capif_onboarding/*
