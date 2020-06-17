Forwart local port 9090 to the prometheus service in the cluster:

    kubectl port-forward -n NAMESPACE service/prometheus-server 9090:80
