import router from 'girder/router';
import events from 'girder/events';

import DataflowModel from './models/DataflowModel';
import DataflowListView from './views/DataflowListView';
import DataflowView from './views/DataflowView';
import CreateDataflowView from './views/CreateDataflowView';

router.route('dataflows', 'dataflows', function () {
    events.trigger('g:navigateTo', DataflowListView);
});

router.route('newdataflow', 'newdataflow', () => {
    events.trigger('g:navigateTo', CreateDataflowView);
});

router.route('dataflow/:id/edit', 'newdataflow', (id, params) => {
    const itemTask = new DataflowModel({_id: id});
    const promises = [itemTask.fetch()];

    $.when(...promises).done(() => {
        let initialValues = {};

        events.trigger('g:navigateTo', CreateDataflowView, {
            model: itemTask,
            initialValues: initialValues
        }, {
            renderNow: true
        });
    }).fail(() => {
        router.navigate('dataflows', {trigger: true, replace: true});
    });
});

router.route('dataflow/:id', 'dataflow', function (id, params) {
    const item = new DataflowModel({_id: id});
    const promises = [item.fetch()];

    $.when(...promises).done(() => {
        events.trigger('g:navigateTo', DataflowView, {
            model: item
        }, {
            renderNow: true
        });
    }).fail(() => {
        router.navigate('dataflows', {trigger: true, replace: true});
    });
});
