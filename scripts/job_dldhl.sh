#!/bin/bash
YEAR=$1

TIMESTAMP="$(date +%s)"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <year>"
    exit 1
fi

sed s/"YEAR"/$YEAR/g k8s/download_drought_job.tmpl | sed s/"TS"/$TIMESTAMP/g > download_drought_job_$YEAR-$TIMESTAMP.yaml
kubectl apply -f download_drought_job_$YEAR-$TIMESTAMP.yaml
rm download_drought_job_$YEAR-$TIMESTAMP.yaml