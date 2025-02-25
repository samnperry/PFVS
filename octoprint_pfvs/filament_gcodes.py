from collections import namedtuple

def generate_gcode(settings):
    return [
        "M104 S{}".format(settings['print_temp']),
        "M140 S{}".format(settings['bed_temp']),
    ]

# Define the immutable scan object
MaterialScan = namedtuple("MaterialScan", ["name", "wavelengths", "intensities", "settings"])

# Settings Arrays
FILAMENT_SETTINGS = {
    "PLA": {
        "print_temp": 210,
        "bed_temp": 60,
    },
    "PETG": {
        "print_temp": 240,
        "bed_temp": 85,
    },
    "ASA": {
        "print_temp": 260,
        "bed_temp": 100,
    },
}