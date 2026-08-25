#!/bin/bash
YEAR=$1
MONTH=$2

TIMESTAMP="$(date +%s)"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <year> <month>"
    exit 1
fi

sed s/"YEAR"/$YEAR/g k8s/backfill_job.tmpl | sed s/"MONTH"/$MONTH/g | sed s/"TS"/$TIMESTAMP/g > backfill_job_$YEAR-$MONTH-$TIMESTAMP.yaml
kubectl apply -f backfill_job_$YEAR-$MONTH-$TIMESTAMP.yaml
rm backfill_job_$YEAR-$MONTH-$TIMESTAMP.yaml