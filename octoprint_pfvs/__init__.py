# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
import time

class PFVSPlugin(octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.OctoPrintPlugin
):

    def __init__(self):
        super().__init__()
        self.is_filament_loading = False
        self.is_filament_unloading = False

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
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
        if event == Events.PRINT_STARTED:
            # Pause the print
            self._printer.pause_print()
            self._logger.info("Print started - pausing for 30 seconds.")
            
            # Resume the print
            self._printer.resume_print()
            self._logger.info("Resuming print after 30 second pause.")

    ##~~ G-code received hook

        ##~~ G-code received hook

    def process_gcode(self, comm, line, *args, **kwargs):
        # Check if the line contains filament loading/unloading commands
        if "M701" in line:
            self.is_filament_loading = True
            self.is_filament_unloading = False
            self._logger.info("Filament is being loaded.")

        elif "M702" in line:
            self.is_filament_loading = False
            self.is_filament_unloading = True
            self._logger.info("Filament is being unloaded.")

        # If neither, reset flags
        else:
            self.is_filament_loading = False
            self.is_filament_unloading = False

        return line


    ##~~ Softwareupdate hook

    def get_update_information(self):
        return {
            "pfvs": {
                "displayName": "PFVS Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "samnperry",
                "repo": "PFVS",
                "current": self._plugin_version,

                # update method: pip
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
