import $ from 'jquery';
import _ from 'underscore';

import DataflowModel from '../models/DataflowModel';
import SpecModel from '../models/SpecModel';
import CreateDataflowViewTemplate from '../templates/createDataflowView.pug';
// import ScriptAddWidget from '../widgets/ScriptAddWidget';
import '../stylesheets/createDataflowView.styl';

import '@girder/core/utilities/jquery/girderEnable';

const { restRequest } = girder.rest;
const router = girder.router;
const FolderModel = girder.models.FolderModel;
const MarkdownWidget = girder.views.widgets.MarkdownWidget;
const BrowserWidget = girder.views.widgets.BrowserWidget;
const View = girder.views.View;
const { getCurrentUser } = girder.auth;

var lastParent = null;
var lastParentSource = null;

var CreateDataflowView = View.extend({
    events: {
        'submit #g-item-edit-form': function () {
            this.$('.form-group').removeClass('has-error');
            var scripts = [];
            scripts.forEach.call(document.getElementsByClassName('g-script'), function (el) {
                scripts.push(el.value);
            });
            var fields = {
                name: this.$('#g-name').val(),
                description: this.descriptionEditor.val(),
                spec: {
                    destinationId: this.$('#g-folder-data-id').attr('objId'),
                    sourceId: this.$('#g-folder-source-id').attr('objId') || null,
                    image: this.$('button.g-dataflow-frontend-select:first-child').val(),
                    type: this.$('#g-item-edit-form .radio input:checked').val(),
                    topic: this.$('#g-topic-name').val().trim()
                }
            };

            if (this.dataflow) {
                this.updateDataflow(fields);
            } else {
                this.createDataflow(fields);
            }

            this.descriptionEditor.saveText();
            this.$('button.g-save-item').girderEnable(false);
            this.$('.g-validation-failed-message').empty();
            return false;
        },
        'click .g-open-browser': '_openBrowser',
        'click .g-open-browser-src': '_openBrowserSrc',
        'click a.g-frontend': function (e) {
            var frontendName = $(e.currentTarget).text();
            $('button.g-dataflow-frontend-select:first-child').text(frontendName);
            $('button.g-dataflow-frontend-select:first-child').val(frontendName);
        },
        'click a.g-dataflow-type': function (e) {
            var frontendName = $(e.currentTarget).text();
            $('button.g-dataflow-type-select:first-child').text(frontendName);
            $('button.g-dataflow-type-select:first-child').val(frontendName);
        },
        'click button.g-script-add-button': function (e) {
            e.preventDefault();
            this.addNewScript(e);
        },
        'click a.g-cancel-dataflow': function (e) {
            router.navigate('/dataflows', {trigger: true});
        },
        'change #g-item-edit-form .radio input': 'typeChanged'
    },

    initialize: function (settings) {
        this.dataflow = settings.model || null;
        this.initialValues = settings.initialValues || null;
        this.descriptionEditor = new MarkdownWidget({
            text: this.dataflow ? this.dataflow.get('description') : '',
            prefix: 'item-description',
            placeholder: 'Enter a description',
            enableUploads: false,
            parentView: this
        });
        this.dataSelector = new BrowserWidget({
            parentView: this,
            showItems: false,
            selectItem: false,
            root: lastParent || getCurrentUser(),
            titleText: this.initialValues ? this.initialValues.data : 'Select a folder for upload',
            helpText: 'Browse to a directory to select it, then click "Save"',
            showPreview: false,
            input: this.initialValues ? {default: this.initialValues.data} : false,
            validate: _.noop
        });
        this.sourceSelector = new BrowserWidget({
            parentView: this,
            showItems: false,
            selectItem: false,
            root: lastParentSource || getCurrentUser(),
            titleText: this.initialValues ? this.initialValues.source : 'Select a folder with source',
            helpText: 'Browse to a directory to select it, then click "Save"',
            showPreview: false,
            input: this.initialValues ? {default: this.initialValues.sourceId} : false,
            validate: _.noop
        });

        if (this.dataflow) {
            const spec = this.dataflow.attributes.spec;
            if (spec.image) {
                this.initialValues.image = spec.image;
            }
            if (spec.topic && spec.type === 'openmsi') {
                this.initialValues.topic = spec.topic;
            }
            if (spec.destinationId) {
                const destinationFolder = new FolderModel({_id: spec.destinationId});
                destinationFolder.fetch().done(() => {
                    lastParent = destinationFolder.parentId;
                    this.dataSelector.root = destinationFolder;
                    this.$('#g-folder-data-id').val(destinationFolder.get('name'));
                    this.$('#g-folder-data-id').attr('objId', destinationFolder.id);
                });
            }
            if (spec.sourceId) {
                const sourceFolder = new FolderModel({_id: spec.sourceId});
                sourceFolder.fetch().done(() => {
                    lastParentSource = sourceFolder.parentId;
                    this.sourceSelector.root = sourceFolder;
                    this.$('#g-folder-source-id').val(sourceFolder.get('name'));
                    this.$('#g-folder-source-id').attr('objId', sourceFolder.id);
                });
            }
            if (spec.type) {
                this.initialValues.type = spec.type;
                this.$('#g-item-edit-form .radio input[value="' + spec.type + '"]').prop('checked', true);
            }
        }

        this.listenTo(this.dataSelector, 'g:saved', function (val) {
            this.$('#g-folder-data-id').val(val.attributes.name);
            this.$('#g-folder-data-id').attr('objId', val.id);
        });

        this.listenTo(this.sourceSelector, 'g:saved', function (val) {
            this.$('#g-folder-source-id').val(val.attributes.name);
            this.$('#g-folder-source-id').attr('objId', val.id);
        });

        restRequest({
            url: 'dataflow/images'
        }).done((resp) => {
            this.images = resp;
            this.render();
        });
    },

    addNewScript: function (event) {
        var newRow = $('<div>').attr({
            class: 'g-script-row'
        }).appendTo(this.$el.find('.g-scripts-container'));

        /* new ScriptAddWidget({
            el: newRow,
            item: this.item,
            parentView: this
        }).render(); */

        if (_.isString(event)) {
            newRow[0].children[0].children[0].value = event; // Ugly isn't it?
        }
    },

    typeChanged: function () {
        const type = this.$('#g-item-edit-form .radio input:checked').val();
        if (type === 'dagster') {
            this.$('#g-topic-name').attr('disabled', true);
            this.$('#g-topic-name').attr('placeholder', 'Dataflow topic is not used for dagster');
            this.$('#g-folder-source-id').attr('disabled', false);
            this.$('.g-open-browser-src').attr('disabled', false);
        } else {
            this.$('#g-topic-name').attr('disabled', false);
            this.$('#g-topic-name').attr('placeholder', 'Enter a topic name');
            this.$('#g-folder-source-id').attr('disabled', true);
            this.$('.g-open-browser-src').attr('disabled', true);
        }
    },

    render: function () {
        this.$el.html(CreateDataflowViewTemplate({
            item: this.dataflow,
            images: this.images,
            frontends: []
        }));
        this.descriptionEditor.setElement(this.$('.g-description-editor-container')).render();

        if (this.dataflow) {
            this.$('#g-name').val(this.dataflow.attributes.name);
        }
        if (this.initialValues) {
            $('button.g-dataflow-frontend-select:first-child').text(this.initialValues.image);
            $('button.g-dataflow-frontend-select:first-child').val(this.initialValues.image);
            this.$('#g-topic-name').val(this.initialValues.topic);
            this.$('#g-folder-data-id').val(this.initialValues.destinationId);
            this.$('#g-folder-source-id').val(this.initialValues.sourceId);
            this.$('#g-item-edit-form .radio input[value="' + this.initialValues.type + '"]').prop('checked', true);
        }
        this.typeChanged();
        return this;
    },

    _openBrowser: function () {
        this.dataSelector.setElement($('#g-dialog-container')).render();
    },

    _openBrowserSrc: function () {
        this.sourceSelector.setElement($('#g-dialog-container')).render();
    },

    createDataflow: function (fields) {
        fields.spec = JSON.stringify(fields.spec);
        var dataflow = new DataflowModel();
        dataflow.set(_.extend(fields, {}));
        dataflow.on('g:saved', function () {
            this.trigger('g:saved', dataflow);
            router.navigate('/dataflows', {trigger: true});
        }, this).on('g:error', function (err) {
            this.$('.g-validation-failed-message').text(err.responseJSON.message);
            this.$('button.g-save-item').girderEnable(true);
            this.$('#g-' + err.responseJSON.field).focus();
        }, this).save();
    },

    updateDataflow: function (fields) {
        if (fields.spec !== this.dataflow.attributes.spec) {
            // If the spec changed, we need to update the spec
            const spec = new SpecModel({dataflowId: this.model.id, data: JSON.stringify(fields.spec)});
            spec.on('g:saved', function () {
                console.log('Spec saved');
            }, this).on('g:error', function (err) {
                this.dataflow.trigger('g:error', err);
            }, this).save();
        }

        this.dataflow.set('name', fields.name);
        this.dataflow.set('description', fields.description);

        this.dataflow.off().on('g:saved', function () {
            this.$el.modal('hide');
            this.trigger('g:saved', this.dataflow);
            router.navigate(`/dataflow/${this.dataflow.id}`, {trigger: true});
        }, this).on('g:error', function (err) {
            this.$('.g-validation-failed-message').text(err.responseJSON.message);
            this.$('button.g-save-item').girderEnable(true);
            this.$('#g-' + err.responseJSON.field).focus();
        }, this).save();
    }
});

export default CreateDataflowView;
