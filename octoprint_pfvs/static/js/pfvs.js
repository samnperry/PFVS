/*
 * View model for Plastic Filament Verification System
 *
 * Author: Team 25009
 * License: AGPLv3
 */
$(function() {
    function PfvsViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
        self.spectrometerData = ko.observableArray([]);
        self.isSpectrometerRunning = ko.observable(false);

        self.startSpectrometer = function () {
            $.ajax({
                url: "/plugin/pfvs/start_spectrometer",
                type: "POST",
                success: function (response) {
                    console.log(response.status)
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
