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

        if (this._dataflowSpec.sourceId) {
            promises.push(restRequest({
                url: 'resource/' + this._dataflowSpec.sourceId + '/path',
                type: 'GET',
                data: {
                    type: 'folder'
                }
            }).then((resp) => resp));
            promises.push(restRequest({
                url: `folder/${this._dataflowSpec.sourceId}`
            }).then((resp) => resp));
        }

        var view = this;
        // Fetch the plugin list
        $.when(...promises).done(function () {
            view.scripts = [];
            if (arguments.length > 2) {
                view.sourcePath = arguments[2];
                let srcFolder = arguments[3];
                view.sourceLink = `#${srcFolder.baseParentType}/${srcFolder.baseParentId}/folder/${srcFolder._id}`;
            }
            view.destinationPath = arguments[0];
            let dstFolder = arguments[1];
            view.destinationLink = `#${dstFolder.baseParentType}/${dstFolder.baseParentId}/folder/${dstFolder._id}`;
            view.render();
        }).fail(() => {
            router.navigate('/', { trigger: true });
        });
    },

    render: function () {
        this.$el.html(template({
            dataflow: this.model,
            dstPath: this.destinationPath,
            dstLink: this.destinationLink,
            srcPath: this.sourcePath || null,
            srcLink: this.sourceLink || null,
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
