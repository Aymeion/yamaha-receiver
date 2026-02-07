import requests
import xml.etree.ElementTree as ET


class YamahaReceiver:
    def __init__(self, ip, zone="Main_Zone"):
        self.ip = ip
        self.zone = zone
        self.url = f"http://{self.ip}/YamahaRemoteControl/ctrl"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "text/xml; charset=utf-8",
                "User-Agent": "Python/YamahaController",
            }
        )

    def _send_command(self, xml_body, cmd_type="PUT"):
        """Centralized method to send XML to the receiver."""
        payload = (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<YAMAHA_AV cmd="{cmd_type}">'
            f"<{self.zone}>{xml_body}</{self.zone}>"
            f"</YAMAHA_AV>"
        )
        try:
            response = self.session.post(
                self.url, data=payload.encode("utf-8"), timeout=5
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Communication Error: {e}")
            return None

    def set_power(self, turn_on=True):
        action = "On" if turn_on else "Standby"
        xml = f"<Power_Control><Power>{action}</Power></Power_Control>"
        return self._send_command(xml)

    def set_input(self, input_name):
        xml = f"<Input><Input_Sel>{input_name}</Input_Sel></Input>"
        return self._send_command(xml)

    def get_volume(self):
        xml = "<Basic_Status>GetParam</Basic_Status>"
        response_text = self._send_command(xml, cmd_type="GET")
        if response_text:
            root = ET.fromstring(response_text)
            val = root.find(".//Volume/Lvl/Val").text
            return int(val) / 10.0
        return None

    def set_volume(self, db_level, safety=True):
        # Yamaha integer conversion
        yamaha_val = int(db_level * 10)
        if safety:
            yamaha_val = min(yamaha_val, -300)  # Max safety limit -30dB

        xml = (
            f"<Volume><Lvl><Val>{yamaha_val}</Val>"
            f"<Exp>1</Exp><Unit>dB</Unit></Lvl></Volume>"
        )
        return self._send_command(xml)

    def adjust_volume(self, increment, safety=True):
        current = self.get_volume()
        if current is not None:
            self.set_volume(current + increment, safety)


if __name__ == "__main__":
    amp = YamahaReceiver("192.168.51.156")

    amp.set_power(True)
    amp.set_input("HDMI2")

    print(f"Volume is: {amp.get_volume()} dB")
    amp.adjust_volume(5)  # Increase by 5dB
