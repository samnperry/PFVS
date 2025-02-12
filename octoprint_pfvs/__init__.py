from __future__ import absolute_import
import time
import octoprint.plugin
from octoprint.events import Events
import threading
import re
import sys
import os
import math
from flask import jsonify
from octoprint_pfvs import spectrometer as spect

class PFVSPlugin(octoprint.plugin.SettingsPlugin,
                 octoprint.plugin.AssetPlugin,
                 octoprint.plugin.TemplatePlugin,
                 octoprint.plugin.EventHandlerPlugin,
                 octoprint.plugin.BlueprintPlugin,
                 octoprint.plugin.OctoPrintPlugin):

    def __init__(self):
        super().__init__()
        self.is_filament_loading = False
        self.is_filament_unloading = False
        self.arduino_serial = None
        self.serial_thread = None
        self.running = False
        self.print_paused = False
        self.spectrometer_thread = None
        self.spectrometer_running = False  # Flag to control the spectrometer thread

    def on_after_startup(self):
        self._logger.info("PFVS Plugin initialized.")
        try:
            spect.init()
            self._logger.info("Spectrometer initialized successfully.")
        except Exception as e:
            self._logger.error(f"Failed to initialize spectrometer: {e}")

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {}

    ##~~ AssetPlugin mixin

    def get_assets(self):
        return {
            "js": ["js/pfvs.js"],
            "css": ["css/pfvs.css"],
            "less": ["less/pfvs.less"]
        }

    ##~~ TemplatePlugin mixin

    def get_template_vars(self):
        return {"plugin_version": self._plugin_version}
    
    ##~~ Template Plugin Mixin
    def get_template_configs(self):
        return [
            {
                "type": "tab", 
                "name": "PFVS",
                "template": "pfvs.jinja2",
            },
            {
            "type": "generic",
            "template": None,  # Prevents loading anywhere else
            }
        ]

    ##~~ Event Handler Plugin

    def on_event(self, event, payload):
        self._logger.info(f"Event received: {event}")
        
        if event == "PrinterStateChanged":
            new_state = payload.get("state_id")
            self._logger.info(f"New printer state: {new_state}")

            if new_state == "PRINTING":
                self._logger.info("Print has officially started.")
                self.print_started = True  # Set flag when print starts

    def delayed_resume_print(self):
        time.sleep(30)
        self._printer.resume_print()
        self.print_paused = False  
        self._logger.info("Resuming print after 30-second pause.")

    ##~~ G-code received hook

    def process_gcode(self, comm, line, *args, **kwargs):
        """ Processes received G-code and handles temperature adjustments """
        
        # Detect filament loading/unloading commands
        if "M701" in line:  
            self.is_filament_loading = True
            self.is_filament_unloading = False
            self._logger.info("Filament is being loaded.")
        elif "M702" in line:  
            self.is_filament_loading = False
            self.is_filament_unloading = True
            self._logger.info("Filament is being unloaded.")
        else:
            self.is_filament_loading = False
            self.is_filament_unloading = False
            
        # Extract temperatures from the G-code line
        match = re.search(r'(\d+\.?\d*)/(\d+\.?\d*)', line)    
        if match:
            current_temp = float(match.group(1))  
            target_temp = float(match.group(2))
            filament_test_load = 220.0  # The correct test temperature

            # Check if we are close to the target temperature
            if self.print_started and current_temp >= 0.95 * target_temp:
                # If target temperature is incorrect, adjust it first
                if not math.isclose(target_temp, filament_test_load, rel_tol=1e-2):  
                    self._logger.info(f"Incorrect target temperature detected: {target_temp}°C. Changing to {filament_test_load}°C.")

                    # Set hotend temperature and wait for stabilization
                    self._printer.commands([f"M104 S{filament_test_load}", f"M109 S{filament_test_load}"])
                    
                    # Ensure the new temperature is reached before pausing
                    self._logger.info(f"Waiting for temperature stabilization at {filament_test_load}°C before pausing...")
                
                # Now pause the print
                self._printer.pause_print()
                self._logger.info(f"Print paused - current temperature: {current_temp}°C, target: {target_temp}°C.")

                # Start a separate thread to resume after 30 seconds
                threading.Thread(target=self.delayed_resume_print, daemon=True).start()
            
        return line

    ##~~ Spectrometer Handling

    def start_spectrometer(self):
        """Starts a separate thread for reading spectrometer data."""
        if self.spectrometer_running:
            self._logger.info("Spectrometer is already running.")
            return
        
        self.spectrometer_running = True
        self.spectrometer_thread = threading.Thread(target=self.read_spectrometer_data, daemon=True)
        self.spectrometer_thread.start()
        self._logger.info("Spectrometer data collection started.")

    def stop_spectrometer(self):
        """Stops the spectrometer thread."""
        self.spectrometer_running = False
        self._logger.info("Stopping spectrometer data collection.")

    def read_spectrometer_data(self):
        """Reads data from the spectrometer and sends it to the web interface."""
        try:
            spect.setGain(3)  
            while self.spectrometer_running:
                CALvalues = spect.readCAL()

                # Send data to web UI
                self._plugin_manager.send_plugin_message(self._identifier, {"spectrometer_data": CALvalues})
                
                time.sleep(1)  # Adjust sampling rate
        except Exception as e:
            self._logger.error(f"Error reading spectrometer data: {e}")

    ##~~ Software update hook

    def get_update_information(self):
        return {
            "pfvs": {
                "displayName": "PFVS Plugin",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "samnperry",
                "repo": "PFVS",
                "current": self._plugin_version,
                "pip": "https://github.com/samnperry/PFVS/archive/{target_version}.zip",
            }
        }

    ##~~ API for UI to Start/Stop Spectrometer

    @octoprint.plugin.BlueprintPlugin.route("/start_spectrometer", methods=["POST"])
    def api_start_spectrometer(self):
        """API endpoint to start spectrometer via UI."""
        self.start_spectrometer()
        return jsonify(status="Spectrometer started")

    @octoprint.plugin.BlueprintPlugin.route("/stop_spectrometer", methods=["POST"])
    def api_stop_spectrometer(self):
        """API endpoint to stop spectrometer via UI."""
        self.stop_spectrometer()
        return jsonify(status="Spectrometer stopped")

__plugin_name__ = "PFVS Plugin"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PFVSPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.received": (__plugin_implementation__.process_gcode, 1),
    }
