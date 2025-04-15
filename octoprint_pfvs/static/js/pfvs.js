/*
 * View model for Plastic Filament Verification System
 *
 * Author: Team 25009
 * License: AGPLv3
 */
$(function() {
    function PfvsViewModel(parameters) {
        var self = this;

        self.spectrometerData = ko.observableArray([]);
        self.isSpectrometerRunning = ko.observable(false);
        self.predictedMaterial = ko.observable("");
        self.filamentType = ko.observable("");
        self.filamentColor = ko.observable("");

        self.saveFilamentMetadata = function() {
            const type = self.filamentType().trim();
            const color = self.filamentColor().trim();

            if (!type || !color) {
                alert("Please enter both filament type and color.");
                return;
            }

            // You can process the metadata here
            console.log("Filament Type: " + type);
            console.log("Filament Color: " + color);

            // Here you might want to send the data to a server or process it further
            $.ajax({
                url: "/plugin/pfvs/save_filament_metadata",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    type: type,
                    color: color
                }),
                success: function(response) {
                    console.log("Metadata saved:", response.status);
                    // You can provide feedback to the user (e.g., success message)
                },
                error: function() {
                    console.error("Failed to save filament metadata.");
                    // Handle error, e.g., show a message to the user
                }
            });
        };

        self.startSpectrometer = function () {
            const type = self.filamentType().trim();
            const color = self.filamentColor().trim();

            if (!type || !color) {
                alert("Please enter both filament type and color before starting the spectrometer.");
                return;
            }

            $.ajax({
                url: "/plugin/pfvs/start_spectrometer",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    type: type,
                    color: color
                }),
                success: function (response) {
                    console.log(response.status);
                    self.isSpectrometerRunning(true);
                },
                error: function () {
                    console.error("Failed to start spectrometer.");
                }
            });
        };

        self.stopSpectrometer = function () {
            $.ajax({
                url: "/plugin/pfvs/stop_spectrometer",
                type: "POST",
                success: function (response) {
                    console.log(response.status);
                    self.isSpectrometerRunning(false);
                },
                error: function () {
                    console.error("Failed to stop spectrometer.");
                }
            });
        };

        // Listen for real-time spectrometer data
        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin !== "pfvs") return;

            if (data.spectrometer_data) {
                self.spectrometerData(data.spectrometer_data);
            }

            if (data.predicted_material) {  // Update predicted material
                self.predictedMaterial(data.predicted_material);
            }
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: PfvsViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_pfvs, #tab_plugin_pfvs, ...
        elements: ["#pfvs_plugin"]
    });
});
