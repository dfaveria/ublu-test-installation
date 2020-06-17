Grafana is provisioned with a default admin user (password: 'secret'). Please do not expose Grafana with a Route/Ingress
as long as you do not patch this password to a more secure value!

## Access to Grafana using port forwarding

Forwart local port 3000 to the Grafana service in the cluster:

    kubectl port-forward -n NAMESPACE service/grafana 3000:80
