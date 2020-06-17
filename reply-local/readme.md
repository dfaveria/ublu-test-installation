# Install the OC Client
Download the latest 'oc' client from https://www.openshift.org/download.html and
 and install according to the instructions for your OS.

# Log in to your cluster

```sh
oc login https://console.example.com/
```
where you will be prompted for your username or
```sh
oc login https://console.example.com/ -u <username> [-p <password>]
```

# Select project (namespace)

```sh
# list projects
oc projects
```

```#!/bin/sh
oc project example_openshift
```

Next commands refer to the cluster (from the oc login command above) for the project (from the oc project command). 

# Deploy

Initial setup: (run only once)

```sh
oc apply -f gcr-secret.yaml
```

(Re-)Deploy Unblu:

```sh
./kustomize build example_openshift | oc apply -f -
```

Delete everything:

```sh
./kustomize build example_openshift | oc delete -f -
```

Delete only ZooKeeper, Kafka, and the Collaboration Server:

```sh
oc delete deployments,statefulsets,pods --grace-period=0 --force -l "component in (zookeeper, kafka, collaboration-server)"
```
