from collections import namedtuple

def generate_gcode(settings):
    return [
        f"M104 S{settings['print_temp']}",
        f"M140 S{settings['bed_temp']}",
        f"M106 S{int(settings['fan_speed'] * 2.55)}",
        f"M220 S{settings['print_speed']}",
        f"M207 S{settings['retraction_distance']} F{settings['retraction_speed']}",
        f"M211 Z{settings['z_hop']}",
        f"M221 S{settings['flow_rate']}",
        f"M218 Z{settings['infill_percentage']}",
        "M302 P1" if settings['requires_enclosure'] else "M302 P0"
    ]

# Define the immutable scan object
MaterialScan = namedtuple("MaterialScan", ["name", "wavelengths", "intensities", "settings"])

# Settings Arrays
FILAMENT_SETTINGS = {
    "PLA": {
        "print_temp": 200,
        "bed_temp": 60,
        "fan_speed": 100,
        "print_speed": 50,
        "retraction_distance": 1.5,
        "retraction_speed": 35,
        "z_hop": 0.2,
        "flow_rate": 100,
        "infill_percentage": 20,
        "requires_enclosure": False,
    },
    "PETG": {
        "print_temp": 240,
        "bed_temp": 80,
        "fan_speed": 50,
        "print_speed": 40,
        "retraction_distance": 6.0,
        "retraction_speed": 25,
        "z_hop": 0.4,
        "flow_rate": 105,
        "infill_percentage": 30,
        "requires_enclosure": False,
    },
    "ASA": {
        "print_temp": 240,
        "bed_temp": 100,
        "fan_speed": 0,
        "print_speed": 50,
        "retraction_distance": 2.0,
        "retraction_speed": 30,
        "z_hop": 0.2,
        "flow_rate": 100,
        "infill_percentage": 20,
        "requires_enclosure": True,
    },
}