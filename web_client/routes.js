import router from 'girder/router';
import events from 'girder/events';
import { exposePluginConfig } from 'girder/utilities/PluginUtils';

import DataflowModel from './models/DataflowModel';
import ConfigView from './views/ConfigView';
import DataflowListView from './views/DataflowListView';
import DataflowView from './views/DataflowView';
import CreateDataflowView from './views/CreateDataflowView';

exposePluginConfig('dataflows', 'plugins/dataflows/config');

router.route('plugins/dataflows/config', 'dataflowsConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});

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
