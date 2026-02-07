import requests

IP = "192.168.51.156"

def yamaha_switch(switch = True, ip_address = IP):
    url = f"http://{ip_address}/YamahaRemoteControl/ctrl"
    action = "Standby"
    if switch:
        action = "On"
        
    
    # Use a raw multi-line string for the XML payload
    # This matches the ID "P1" mapping in desc.xml: Main_Zone -> Power_Control -> Power
    xml_payload = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<YAMAHA_AV cmd="PUT">'
        '<Main_Zone>'
        '<Power_Control>'
        f'<Power>{action}</Power>'
        '</Power_Control>'
        '</Main_Zone>'
        '</YAMAHA_AV>'
    )

    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'User-Agent': 'Python/Requests'
    }

    try:
        # It's important to send the data as bytes to ensure precise formatting
        response = requests.post(
            url, 
            data=xml_payload.encode('utf-8'), 
            headers=headers,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")

def yamaha_set_input(input_name, ip_address = IP):
    url = f"http://{ip_address}/YamahaRemoteControl/ctrl"
    
    # XML payload to change the input
    # Path derived from P4 in desc.xml: Main_Zone -> Input -> Input_Sel
    xml_payload = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<YAMAHA_AV cmd="PUT">'
        '<Main_Zone>'
        '<Input>'
        f'<Input_Sel>{input_name}</Input_Sel>'
        '</Input>'
        '</Main_Zone>'
        '</YAMAHA_AV>'
    )

    headers = {'Content-Type': 'text/xml; charset=utf-8'}

    try:
        response = requests.post(url, data=xml_payload.encode('utf-8'), headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    yamaha_switch(True)
    yamaha_set_input("HDMI2")