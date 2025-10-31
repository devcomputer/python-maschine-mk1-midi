#!/usr/bin/env python3
from evdev import InputDevice, ecodes
import rtmidi
import signal
import sys

# ----- CONFIG -----
DEVICE_PATH = "/dev/input/event10"  # your Maschine event device -> figure it out using: $sudo evtest
# your mapping might differ. i only have one device to test. to figure out your keys using $sudo evtest and selecting the Maschine Controller
# then hit the pads and note down the "codes" for each pad.
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
dev = InputDevice(DEVICE_PATH)

midiout = rtmidi.MidiOut()
midiout.open_virtual_port("Maschine MK1 MIDI")
print(f"Listening on {DEVICE_PATH}")
print("Virtual MIDI port: Maschine MK1 MIDI")

# store last sent velocity per pad to avoid flooding
last_velocity = {code: -1 for code in PAD_MAP}

# graceful exit
def signal_handler(sig, frame):
    print("Exiting...")
    midiout.close_port()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ----- MAIN LOOP -----
for event in dev.read_loop():
    if event.type == ecodes.EV_ABS and event.code in PAD_MAP:
        pad_note = PAD_MAP[event.code]
        velocity = event.value

        # scale velocity from Maschine range (~0–2300) to MIDI 0–127
        velocity_midi = max(0, min(127, int(velocity / 18)))

        # only send if velocity changed
        if velocity_midi != last_velocity[event.code]:
            if velocity_midi > 0:
                # Note ON
                midiout.send_message([0x90, pad_note, velocity_midi])
                print(f"Pad {event.code-35:02} -> Note {pad_note} ON, vel {velocity_midi}")
            else:
                # Note OFF
                midiout.send_message([0x80, pad_note, 0])
                print(f"Pad {event.code-35:02} -> Note {pad_note} OFF")

            last_velocity[event.code] = velocity_midi
