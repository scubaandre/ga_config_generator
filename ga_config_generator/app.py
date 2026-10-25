import streamlit as st
import requests
import os
import yaml

st.set_page_config(layout="wide")
st.title("Google Assistant Config Generator")

# Home Assistant automatically injects SUPERVISOR_TOKEN into local add-ons
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")
HA_URL = "http://supervisor/core/api/states" # Direct internal network routing

@st.cache_data(ttl=60)
def fetch_ha_entities():
    if not SUPERVISOR_TOKEN:
        return []
    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "content-type": "application/json",
    }
    try:
        response = requests.get(HA_URL, headers=headers)
        if response.status_code == 200:
            return [item['entity_id'] for item in response.json()]
    except Exception as e:
        st.error(f"Error connecting to Home Assistant API: {e}")
    return []

# 1. Fetch live entities
entities = fetch_ha_entities()

if not entities:
    st.warning("No entities found or unable to communicate with Home Assistant API. (Are you running this inside the HA Add-on environment?)")
    # Fallback mock data for local browser testing outside HA
    entities = ["light.living_room_tv_1", "light.kitchen", "switch.adguard", "camera.front_door", "script.goodnight"]

# 2. Extract and organize unique domains
all_domains = sorted(list(set([e.split('.')[0] for e in entities])))

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. Select Exposed Domains")
    st.write("Which types of devices should Google see by default?")
    
    # Pre-select common safe domains to make it fast
    defaults = ['light', 'switch', 'climate', 'scene', 'media_player', 'script', 'vacuum', 'lock']
    exposed_domains = []
    
    # Dynamic grid layout for domains
    dom_cols = st.columns(4)
    for i, domain in enumerate(all_domains):
        with dom_cols[i % 4]:
            is_default = domain in defaults
            if st.checkbox(f"{domain}", value=is_default, key=f"dom_{domain}"):
                exposed_domains.append(domain)

    st.subheader("2. Filter / Exclude Specific Entities")
    st.write("Uncheck any individual items you want to keep hidden from Google Assistant (e.g. sub-segments, system toggles).")
    
    excluded_entities = []
    
    # Group entities by their domain for cleaner UI
    for domain in exposed_domains:
        domain_entities = [e for e in entities if e.startswith(f"{domain}.")]
        if domain_entities:
            with st.expander(f"Manage {domain} entities ({len(domain_entities)} items)"):
                for entity in domain_entities:
                    if not st.checkbox(f"Expose {entity}", value=True, key=f"ent_{entity}"):
                        excluded_entities.append(entity)

with col2:
    st.subheader("3. Generated `google_assistant.yaml`")
    st.write("Copy this code cleanly directly into your file.")
    
    # Build final yaml dictionary structure
    config_dict = {
        "project_id": "homeassistant-199015",
        "service_account": "!include SERVICE_ACCOUNT.json",
        "report_state": True,
        "expose_by_default": True,
        "exposed_domains": exposed_domains
    }

    if excluded_entities:
        config_dict["entity_config"] = {entity: {"expose": False} for entity in excluded_entities}

    # Format output code box
    yaml_text = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
    # Re-inject the unquoted custom !include string mapping rule
    yaml_text = yaml_text.replace("service_account: '!include SERVICE_ACCOUNT.json'", "service_account: !include SERVICE_ACCOUNT.json")
    
    st.code(yaml_text, language="yaml")
