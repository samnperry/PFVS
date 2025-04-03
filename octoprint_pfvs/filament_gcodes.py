from collections import namedtuple
from typing import Dict, List

class Filament:
    """Class to define filament properties."""
    def __init__(self, name: str, print_temp: int, bed_temp: int):
        self.name = name
        self.print_temp = print_temp
        self.bed_temp = bed_temp

    def generate_gcode(self) -> List[str]:
        """Generate G-code for this filament."""
        return [
            f"M140 S{self.bed_temp}",     # Set bed temp (non-blocking)
            f"M104 S{self.print_temp}",   # Set nozzle temp (non-blocking)
            f"M190 S{self.bed_temp}",     # Wait for bed temp to reach target
            f"M109 S{self.print_temp}",   # Wait for nozzle temp to reach target
        ]

# Define available filament types
FILAMENTS: Dict[str, Filament] = {
    "PLA": Filament("PLA", 210, 60),
    "PET": Filament("PET", 240, 85),
    "ASA": Filament("ASA", 260, 100),
}

# Immutable MaterialScan Object
MaterialScan = namedtuple("MaterialScan", ["name", "wavelengths", "intensities", "settings"])
