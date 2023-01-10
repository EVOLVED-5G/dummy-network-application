
echo "172.17.0.1      capifcore" >> /etc/hosts

curl  --connect-timeout 5 \
    --max-time 10 \
    --retry-delay 0 \
    --retry-max-time 40 \
    --request GET "http://$CAPIF_HOSTNAME:$CAPIF_PORT/ca-root" 2>/dev/null | jq -r '.certificate' -j > ca.crt

tail -f /dev/null