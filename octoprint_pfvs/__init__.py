from __future__ import absolute_import
import time
import octoprint.plugin
from octoprint.events import Events
import serial
import threading

class PFVSPlugin(octoprint.plugin.SettingsPlugin,
                 octoprint.plugin.AssetPlugin,
                 octoprint.plugin.TemplatePlugin,
                 octoprint.plugin.EventHandlerPlugin,
                 octoprint.plugin.OctoPrintPlugin):

    def __init__(self):
        super().__init__()
        self.is_filament_loading = False
        self.is_filament_unloading = False
        self.arduino_serial = None
        self.serial_thread = None
        self.running = False
        
        ##~~ Lifecycle Hooks

    def on_after_startup(self):
        self._logger.info("PFVS Plugin initialized.")

    ##~~ Serial Communication

    # def start_serial_communication(self):
    #     try:
    #         # Open serial port
    #         self.arduino_serial = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)  # Adjust port if needed
    #         self.running = True
    #         self.serial_thread = threading.Thread(target=self.read_from_arduino)
    #         self.serial_thread.start()
    #         self._logger.info("Arduino serial communication started.")
    #     except Exception as e:
    #         self._logger.error(f"Failed to start serial communication: {e}")

    # def read_from_arduino(self):
    #     while self.running:
    #         try:
    #             if self.arduino_serial.in_waiting > 0:
    #                 gcode = self.arduino_serial.readline().decode("utf-8").strip()
    #                 if gcode:  # Ensure valid G-code is received
    #                     self._logger.info(f"Received G-code from Arduino: {gcode}")
    #                     self._printer.commands([gcode])  # Send G-code to the printer
    #         except Exception as e:
    #             self._logger.error(f"Error reading from Arduino: {e}")

    # def stop_serial_communication(self):
    #     self.running = False
    #     if self.serial_thread:
    #         self.serial_thread.join()  # Wait for thread to finish
    #     if self.arduino_serial:
    #         self.arduino_serial.close()  # Close serial connection
    #     self._logger.info("Arduino serial communication stopped.")

    ##~~ Lifecycle Hooks

    # def on_after_startup(self):
    #     self.start_serial_communication()

    # def on_shutdown(self):
    #     self.stop_serial_communication()

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            # Add plugin default settings if needed
        }

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

    ##~~ Event Handler Plugin

    def on_event(self, event, payload):
        self._logger.info(f"Event received: {event}")
        if event == Events.PRINT_STARTED:
            self._printer.pause_print()
            self._logger.info("Print started - pausing for 30 seconds.")

            # Start a thread
            threading.Thread(target=self.delayed_resume_print, daemon=True).start()

    def delayed_resume_print(self):
        time.sleep(30)
        self._printer.resume_print()
        self._logger.info("Resuming print after 30-second pause.")

    ##~~ G-code received hook

    def process_gcode(self, comm, line, *args, **kwargs):
        if "M701" in line:  # Filament loading command
            self.is_filament_loading = True
            self.is_filament_unloading = False
            self._logger.info("Filament is being loaded.")
        elif "M702" in line:  # Filament unloading command
            self.is_filament_loading = False
            self.is_filament_unloading = True
            self._logger.info("Filament is being unloaded.")
        else:
            self.is_filament_loading = False
            self.is_filament_unloading = False

        return line

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

__plugin_name__ = "PFVS Plugin"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PFVSPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.received": (__plugin_implementation__.process_gcode, 1),
    }
