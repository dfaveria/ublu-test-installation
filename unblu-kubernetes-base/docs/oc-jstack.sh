#!/bin/sh

echo "Creating jstack for $1"

PID="$(oc exec $1 -- pgrep -f java)"
oc exec $1 -- jstack -e -l $PID > $1.stack

echo "Created file $1.stack"