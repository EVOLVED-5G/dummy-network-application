curl --request GET 'http://host.docker.internal:8080/ca-root' 2>/dev/null | jq -r '.certificate' -j > ca.crt
cp ca.crt /usr/local/share/ca-certificates/
update-ca-certificates

export REQUESTS_CA_BUNDLE=/usr/src/app/ca.crt
export SSL_CERT_FILE=/usr/src/app/ca.crt

echo '172.17.0.1      capifcore' >> /etc/hosts

tail -f /dev/null