import _ from 'underscore';

import PluginConfigBreadcrumbWidget from 'girder/views/widgets/PluginConfigBreadcrumbWidget';
import View from 'girder/views/View';
import { apiRoot, restRequest } from 'girder/rest';
import events from 'girder/events';

import ConfigViewTemplate from '../templates/configView.pug';
import '../stylesheets/configView.styl';

import 'bootstrap-tagsinput';
import 'bootstrap-tagsinput/dist/bootstrap-tagsinput.css';

var ConfigView = View.extend({
    events: {
        'submit .g-dataflows-config-form': function (event) {
            event.preventDefault();

            var slist = this.SETTING_KEYS.map(function (key) {
                let value = this.$(this.settingControlId(key)).val();
                if (value !== '' && value !== null && value !== undefined) {
                    value = value.trim();
                } else {
                    value = null;
                }
                if (key === 'dataflows.docker_images') {
                    value = this.$('input#g-dataflows-docker-images').tagsinput('items');
                }

                return {
                    key: key,
                    value: value
                };
            }, this);

            this._saveSettings(slist);
        }
    },

    initialize: function () {
        restRequest({
            type: 'GET',
            url: 'system/setting',
            data: {
                list: JSON.stringify(this.SETTING_KEYS)
            }
        }).done(_.bind(function (resp) {
            this.settingVals = resp;
            this.render();
        }, this));
    },

    SETTING_KEYS: [
        'dataflows.kafka_bootstrap_servers',
        'dataflows.kafka_sasl_mechanism',
        'dataflows.kafka_sasl_username',
        'dataflows.kafka_sasl_password',
        'dataflows.kafka_security_protocol',
        'dataflows.dagster_postgres_db',
        'dataflows.dagster_postgres_user',
        'dataflows.dagster_postgres_password',
        'dataflows.docker_images'
    ],

    settingControlId: function (key) {
        return '#g-dataflows-' + key.substring(10).replace(/_/g, '-');
    },

    render: function () {
        var origin = window.location.protocol + '//' + window.location.host;
        var _apiRoot = apiRoot;

        if (apiRoot.substring(0, 1) !== '/') {
            _apiRoot = '/' + apiRoot;
        }

        this.$el.html(ConfigViewTemplate({
            origin: origin,
            apiRoot: _apiRoot
        }));

        if (!this.breadcrumb) {
            this.breadcrumb = new PluginConfigBreadcrumbWidget({
                pluginName: 'Dataflows',
                el: this.$('.g-config-breadcrumb-container'),
                parentView: this
            }).render();
        }

        this.$('#g-dataflows-docker-images').tagsinput();

        if (this.settingVals) {
            for (var i in this.SETTING_KEYS) {
                var key = this.SETTING_KEYS[i];
                if (key === 'dataflows.docker_images') {
                    const images = this.settingVals[key] || [];
                    images.forEach((image) => {
                        this.$('input#g-dataflows-docker-images').tagsinput('add', image);
                    });
                } else {
                    this.$(this.settingControlId(key)).val(this.settingVals[key]);
                }
            }
        }

        return this;
    },

    _saveSettings: function (settings) {
        restRequest({
            type: 'PUT',
            url: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            }
        }).done(_.bind(function () {
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Settings saved.',
                type: 'success',
                timeout: 3000
            });
        }, this)).fail(_.bind(function (resp) {
            this.$('#g-dataflows-config-error-message').text(resp.responseJSON.message);
        }, this));
    }
});

export default ConfigView;
