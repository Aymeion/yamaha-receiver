from yamaha_controller import YamahaReceiver

# --- CONFIGURATION ---
RECEIVER_IP = "192.168.51.156"
TARGET_ZONE = "Main_Zone"


# --- EXAMPLE FUNCTION ---
def main():

    # Initialize the receiver
    amp = YamahaReceiver(RECEIVER_IP, zone=TARGET_ZONE)
    amp.set_power("On")


if __name__ == "__main__":
    main()
