#!/bin/bash


if [ $# -eq 1 ]; then
    TAG="$1"
else
    echo need to include tag to pu
    echo "$0 [TAG]"
    exit -1
fi
scp -r ./backup/$TAG  genoma:/data.lcsc/nfs/personal/dvilas/news/backup/.