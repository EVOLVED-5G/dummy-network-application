#echo "172.17.0.1      capifcore" >> /etc/hosts

#evolved5g register-and-onboard-to-capif --folder_to_store_certificates="/usr/src/app/capif_onboarding" --capif_host="capifcore" --capif_http_port="8080" --capif_https_port="443" --capif_netapp_username="test_netapp22" --capif_netapp_password="test_netapp_password" --capif_callback_url="http://192.168.1.15:5000" --description="test_app_description" --csr_common_name="test_app_common_name" --csr_organizational_unit="test_app_ou" --csr_organization="test_app_o"  --crs_locality="Madrid"  --csr_state_or_province_name="Madrid" --csr_country_name="ES"  --csr_email_address="test@example.com"
evolved5g register-and-onboard-to-capif --config_file_full_path="/usr/src/app/capif_registration.json"

tail -f /dev/null