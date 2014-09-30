#!/bin/bash
#
## by Thibault BRONCHAIN
## (c) 2014 MadeiraCloud LTD.
#

get_vbox_version(){
    local VER
    VER=$(VBoxManage -v | awk -F "r" '{print $1}')
    if [ -z "$VER" ]; then
        echo "ERROR"
    else
        echo "$VER"
    fi
}

write_vbox_dockerfile(){
    local VER
    VER=$(get_vbox_version)
    if [ ! "$LATEST_RELEASE" = "ERROR" ]; then
        sed "s/\$VBOX_VERSION/$VER/g" Dockerfile.tpl > Dockerfile
    else
        echo "WUH WOH"
    fi
}

write_vbox_dockerfile

docker build -t visualops/boot2docker-vbga .
docker run -i -t --rm visualops/boot2docker-vbga /bin/bash &

sleep 2

docker ps --no-trunc=true

echo "Input container ID"
read CID

docker cp $CID:boot2docker.iso boot2docker.iso
