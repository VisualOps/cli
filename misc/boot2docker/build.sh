#!/bin/bash
#
## by Thibault BRONCHAIN
## (c) 2014 MadeiraCloud LTD.
#

docker build -t boot2docker-vbga .
docker run -t --rm boot2docker-vbga > boot2docker.iso
