curl --request GET 'http://host.docker.internal:8080/ca-root' 2>/dev/null | jq -r '.certificate' -j > ca.crt

echo '172.17.0.1      capifcore' >> /etc/hosts

tail -f /dev/null