import View from 'girder/views/View';
import PaginateWidget from 'girder/views/widgets/PaginateWidget';
import router from 'girder/router';

import DataflowCollection from '../collections/DataflowCollection';
import template from '../templates/paginateDataflowsWidget.pug';
import '../stylesheets/paginateDataflowsWidget.styl';

var PaginateDataflowsWidget = View.extend({
    events: {
        'click .g-execute-dataflow-link': function (event) {
            const dataflowId = $(event.currentTarget).data('dataflowId');
            const dataflow = this.collection.get(dataflowId);
            this.trigger('g:selected', {
                dataflow: dataflow
            });
        },
        'click button.g-dataflow-create-button': function (event) {
            router.navigate('newdataflow', {trigger: true});
        }
    },
    /**
     * @param {Function} [settings.dataflowUrlFunc] A callback function, which if provided,
     *        will be called with a single ItemModel argument and should return a string
     *        URL to be used as the dataflow link href.
     * @param {DataflowCollection} [settings.collection] An DataflowCollection for the widget
     *        to display. If no collection is provided, a new DataflowCollection is used.
     */
    initialize: function (settings) {
        this.dataflowUrlFunc = settings.dataflowUrlFunc || null;
        this.collection = settings.collection || new DataflowCollection();
        this.paginateWidget = new PaginateWidget({
            collection: this.collection,
            parentView: this.parentView
        });

        this.listenTo(this.collection, 'g:changed', () => {
            this.render();
        });

        if (settings.collection) {
            this.render();
        } else {
            this.collection.fetch(this.params);
        }
    },

    render: function () {
        this.$el.html(template({
            dataflows: this.collection.toArray(),
            dataflowUrlFunc: this.dataflowUrlFunc
        }));

        this.paginateWidget.setElement(this.$('.g-dataflow-pagination')).render();
        return this;
    }
});

export default PaginateDataflowsWidget;
