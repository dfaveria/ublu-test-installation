# Deploy

Initial setup to create the namespace and add the image pull secret: (run only once)

```sh
kubectl apply -f namespace.yaml
kubectl apply -f gcr-secret.yaml -n example_kubernetes
```

(Re-)Deploy Unblu:

```sh
# run this command from one above the example_kubernetes folder
kustomize build example_kubernetes | kubectl apply -f -
```

Delete everything:

```sh
# run this command from one above the example_kubernetes folder
kustomize build example_kubernetes | kubectl delete -f -
```

Delete only ZooKeeper, Kafka, and the Collaboration Server:
    
```sh
kubectl -n example_kubernetes delete deployments,statefulsets,pods --grace-period=0 --force -l "component in (zookeeper, kafka, collaboration-server)"
```
