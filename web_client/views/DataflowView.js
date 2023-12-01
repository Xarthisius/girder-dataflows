import View from 'girder/views/View';
import { renderMarkdown } from 'girder/misc';
import { restRequest } from 'girder/rest';
import router from 'girder/router';

import template from '../templates/dataflowView.pug';
import '../stylesheets/dataflowView.styl';

const DataflowView = View.extend({
    events: {
        'click .g-reload-dataflow': function (event) {
            this.model.fetch().done(() => { this.render(); });
        },
        'click .g-run-dataflow': function (event) {
            this.execute(event, 'start');
        },
        'click .g-stop-dataflow': function (event) {
            this.execute(event, 'stop');
        },
        'click .g-edit-dataflow': function (event) {
            router.navigate('dataflow/' + this.model.get('_id') + '/edit', {
                params: this._dataflowSpec,
                trigger: true
            });
        }
    },

    initialize: function (settings) {
        this._dataflowSpec = this.model.get('spec');
        const promises = [
            restRequest({
                url: 'resource/' + this._dataflowSpec.destinationId + '/path',
                type: 'GET',
                data: {
                    type: 'folder'
                }
            }).then((resp) => resp),
            restRequest({
                url: `folder/${this._dataflowSpec.destinationId}`
            }).then((resp) => resp)
        ];

        var view = this;
        // Fetch the plugin list
        $.when(...promises).done(function () {
            view.scripts = [];
            if (arguments.length > 2) {
                for (var i = 2; i < arguments.length; i++) {
                    view.scripts.push(arguments[i]);
                }
            }
            view.destinationId = arguments[0];
            let folder = arguments[1];
            view.destinationLink = `#${folder.baseParentType}/${folder.baseParentId}/folder/${folder._id}`;
            view.render();
        }).fail(() => {
            router.navigate('/', { trigger: true });
        });
    },

    render: function () {
        this.$el.html(template({
            dataflow: this.model,
            data: this.destinationId,
            dataLink: this.destinationLink,
            spec: this._dataflowSpec || {},
            renderMarkdown: renderMarkdown
        }));
        return this;
    },

    execute: function (e, action) {
        this.$('.g-validation-failed-message').empty();
        $(e.currentTarget).girderEnable(false);
        restRequest({
            url: 'dataflow/' + this.model.get('_id') + '/execute',
            method: 'PUT',
            data: {
                action: action,
                folderId: this._dataflowSpec.data,
                scripts: JSON.stringify(this._dataflowSpec.scripts)
            },
            error: null
        }).done((resp) => {
            this.model.fetch().done(() => { this.render(); });
        }).fail((resp) => {
            $(e.currentTarget).girderEnable(true);
            this.$('.g-validation-failed-message').text('Error: ' + resp.responseJSON.message);
        });
    }
});

export default DataflowView;
