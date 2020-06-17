#!/bin/sh
set -e

FILTER="component in (collaboration-server, kafka, zookeeper)"
PODS=$(oc get pods --no-headers -l "$FILTER" | awk '{print $1}')

for pod in $PODS 
do
  PID="$(oc exec $pod -- pgrep -f java)"
  oc exec $pod -- jstack -e -l $PID > $pod.stack
  echo "Created file $pod.stack"
done
