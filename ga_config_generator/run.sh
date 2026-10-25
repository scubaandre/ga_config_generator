#!/usr/bin/with-contenv bashio

echo "Starting Google Assistant Config Generator Add-on..."

# Streamlit runs on port 8099, which Ingress will map to your HA UI
python -m streamlit run app.py --server.port 8099 --server.address 0.0.0.0
