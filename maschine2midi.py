#!/usr/bin/env python3

from evdev import InputDevice, ecodes, list_devices


def find_maschine_device(name="Maschine Controller"):
    for dev_path in list_devices():
        dev = InputDevice(dev_path)
        if dev.name == name:
            print(f"Found Maschine device at {dev_path}")
            return dev
    return None


def get_device():
    return find_maschine_device()


import rtmidi
import signal
import sys
import time

# ----- CONFIG -----
DEVICE_PATH = "/dev/input/event24"  # your Maschine event device
# check for correct mapping by running sudo evtest
PAD_MAP = {
    36: 36,  # pad 1  -> C1
    37: 37,  # pad 2  -> C#1
    38: 38,  # pad 3  -> D1
    39: 39,  # pad 4  -> D#1
    32: 40,  # pad 5  -> E1
    33: 41,  # pad 6  -> F1
    34: 42,  # pad 7  -> F#1
    35: 43,  # pad 8  -> G1
    28: 44,  # pad 9  -> G#1
    29: 45,  # pad 10 -> A1
    30: 46,  # pad 11 -> A#1
    31: 47,  # pad 12 -> B1
    24: 48,  # pad 13 -> C2
    25: 49,  # pad 14 -> C#2
    26: 50,  # pad 15 -> D2
    27: 51,  # pad 16 -> D#2
}

# ----- INIT -----
midiout = rtmidi.MidiOut()
midiout.open_virtual_port("Maschine MK1 MIDI")
print("Virtual MIDI port: Maschine MK1 MIDI")

# store last sent velocity per pad to avoid flooding
last_velocity = {code: -1 for code in PAD_MAP}


# graceful exit
def signal_handler(sig, frame):
    print("Exiting...")
    midiout.close_port()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# ----- HELPER -----
def get_device():
    try:
        return InputDevice(DEVICE_PATH)
    except OSError:
        return None


# ----- MAIN LOOP -----
dev = get_device()
while True:
    if dev is None:
        print("Device not found. Waiting...")
        while dev is None:
            time.sleep(1)
            dev = get_device()
        print("Device reconnected!")

    try:
        for event in dev.read_loop():
            if event.type == ecodes.EV_ABS and event.code in PAD_MAP:
                pad_note = PAD_MAP[event.code]
                velocity = event.value

                # scale velocity from Maschine range (~0–2300) to MIDI 0–127
                velocity_midi = max(0, min(127, int(velocity / 18)))

                # only send if velocity changed
                if velocity_midi != last_velocity[event.code]:
                    if velocity_midi > 0:
                        midiout.send_message([0x90, pad_note, velocity_midi])
                        print(
                            f"Pad {event.code - 35:02} -> Note {pad_note} ON, vel {velocity_midi}"
                        )
                    else:
                        midiout.send_message([0x80, pad_note, 0])
                        print(f"Pad {event.code - 35:02} -> Note {pad_note} OFF")

                    last_velocity[event.code] = velocity_midi

    except OSError as e:
        if e.errno == 19:
            print("Device disconnected! Attempting reconnect...")
            dev = None
            continue
        else:
            raise
