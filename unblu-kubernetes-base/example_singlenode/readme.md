This example documents the required patches to run Unblu on a single node.

Even though this is not the recommended way of running a clustered application, some users may choose to do so.

Ingress / Routes to get traffic into the cluster are not part of this example.

# Deploy

Initial setup to create the namespace and add the image pull secret: (run only once)

```sh
kubectl apply -f namespace.yaml
kubectl apply -f gcr-secret.yaml -n singlenode
```

(Re-)Deploy Unblu:

```sh
# run this command from one above the example_singlenode folder
kustomize build example_singlenode | kubectl apply -f -
```

Delete everything:

```sh
# run this command from one above the example_singlenode folder
kustomize build example_singlenode | kubectl delete -f -
```

Delete only ZooKeeper, Kafka, and the Collaboration Server:
    
```sh
kubectl -n singlenode delete deployments,statefulsets,pods --grace-period=0 --force -l "component in (zookeeper, kafka, collaboration-server)"
```
