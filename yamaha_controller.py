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

    def _send_command(self, xml_body, cmd_type="PUT", zone_override=None):
        target_zone = zone_override or self.zone
        payload = (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<YAMAHA_AV cmd="{cmd_type}">'
            f"<{target_zone}>{xml_body}</{target_zone}>"
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

    # --- POWER & SYSTEM ---
    def set_power(self, state="On"):  # Options: On, Standby
        return self._send_command(
            f"<Power_Control><Power>{state}</Power></Power_Control>"
        )

    def set_sleep_timer(self, minutes):  # Options: 30, 60, 90, 120, Off
        val = f"{minutes} min" if minutes != "Off" else "Off"
        return self._send_command(
            f"<Power_Control><Sleep>{val}</Sleep></Power_Control>"
        )

    # --- VOLUME & AUDIO ---
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

    def set_mute(self, enable=True):  # Options: On, Off
        state = "On" if enable else "Off"
        return self._send_command(f"<Volume><Mute>{state}</Mute></Volume>")

    def set_bass(self, level):  # Range: -60 to 60
        return self._send_command(
            f"<Sound_Video><Tone><Bass><Val>{int(level*10)}</Val><Exp>1</Exp><Unit>dB</Unit></Bass></Tone></Sound_Video>"
        )

    def set_treble(self, level):  # Range: -60 to 60
        return self._send_command(
            f"<Sound_Video><Tone><Treble><Val>{int(level*10)}</Val><Exp>1</Exp><Unit>dB</Unit></Treble></Tone></Sound_Video>"
        )

    # --- DSP & SURROUND ---
    def set_sound_program(
        self, program
    ):  # Example: 'Sci-Fi', 'Action Game', '2ch Stereo'
        return self._send_command(
            f"<Surround><Program_Sel><Current><Sound_Program>{program}</Sound_Program></Current></Program_Sel></Surround>"
        )

    def set_straight_mode(self, enable=True):  # Toggle Straight/Surround
        state = "On" if enable else "Off"
        return self._send_command(
            f"<Surround><Program_Sel><Current><Straight>{state}</Straight></Current></Program_Sel></Surround>"
        )

    # --- INPUT & PLAYBACK ---
    def set_input(self, input_name):  # Examples: HDMI1, TUNER, NET RADIO
        return self._send_command(f"<Input><Input_Sel>{input_name}</Input_Sel></Input>")

    def playback_control(
        self, action
    ):  # Options: Play, Pause, Stop, Skip Fwd, Skip Rev
        return self._send_command(
            f"<Play_Control><Playback>{action}</Playback></Play_Control>"
        )

    # --- TUNER (Radio) ---
    def tuner_set_band(self, band):  # Options: AM, FM
        return self._send_command(
            f"<Tuning><Band>{band}</Band></Tuning>", target_zone="Tuner"
        )

    def tuner_set_freq(self, freq, band="FM"):  # FM freq: 8750 (87.50MHz) to 10800
        exp = 2 if band == "FM" else 0
        unit = "MHz" if band == "FM" else "kHz"
        xml = f"<Tuning><Freq><{band}><Val>{freq}</Val><Exp>{exp}</Exp><Unit>{unit}</{band}></Freq></Tuning>"
        return self._send_command(xml, target_zone="Tuner")

    # --- STATUS RETRIEVAL ---
    def get_basic_status(self):
        return self._send_command(
            "<Basic_Status>GetParam</Basic_Status>", cmd_type="GET"
        )

    def get_status(self):
        xml_response = self.get_basic_status()
        if not xml_response:
            return None

        root = ET.fromstring(xml_response)
        status_node = root.find(".//Basic_Status")

        # Helper to safely get text from a nested path
        def find_text(path, default="Unknown"):
            node = status_node.find(path)
            return node.text if node is not None else default

        status = {
            "power": {
                "state": find_text("Power_Control/Power"),
                "sleep": find_text("Power_Control/Sleep"),
            },
            "audio": {
                "volume_db": int(find_text("Volume/Lvl/Val")) / 10.0,
                "mute": find_text("Volume/Mute") == "On",
                "subwoofer_trim": int(find_text("Volume/Subwoofer_Trim/Val")) / 10.0,
                "speaker_a": find_text("Speaker_Preout/Speaker_AB/Speaker_A"),
                "speaker_b": find_text("Speaker_Preout/Speaker_AB/Speaker_B"),
                "extra_bass": find_text("Sound_Video/Extra_Bass"),
            },
            "input": {
                "current": find_text("Input/Input_Sel"),
                "friendly_name": find_text(
                    "Input/Input_Sel_Item_Info/Title"
                ),  # e.g., 'Raspberry Pi'
            },
            "dsp": {
                "program": find_text("Surround/Program_Sel/Current/Sound_Program"),
                "straight": find_text("Surround/Program_Sel/Current/Straight"),
                "enhancer": find_text("Surround/Program_Sel/Current/Enhancer"),
            },
            "tone": {
                "bass": int(find_text("Sound_Video/Tone/Bass/Val")) / 10.0,
                "treble": int(find_text("Sound_Video/Tone/Treble/Val")) / 10.0,
            },
        }
        return status
