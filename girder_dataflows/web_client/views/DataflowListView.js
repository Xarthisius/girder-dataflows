const View = girder.views.View;

import PaginateDataflowsWidget from './PaginateDataflowsWidget';

var DataflowListView = View.extend({
    initialize: function () {
        this.paginateDataflowsWidget = new PaginateDataflowsWidget({
            el: this.$el,
            parentView: this,
            dataflowUrlFunc: (dataflow) => { return `#dataflow/${dataflow.id}`; }
        });
    }
});

export default DataflowListView;
