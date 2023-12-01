import Model from 'girder/models/Model';
import { restRequest } from 'girder/rest';

import SpecCollection from '../collections/SpecCollection';

var DataflowModel = Model.extend({
    resourceName: 'dataflow',

    getSpecs: function () {
        return restRequest({
            url: `${this.resourceName}/${this.id}/specs`
        }).then((resp) => {
            let specCollection = new SpecCollection(resp);
            this.trigger('g:specs', specCollection);
            return specCollection;
        }).fail((err) => {
            this.trigger('g:error', err);
        });
    },

    getHead: function () {
        return restRequest({
            url: `${this.resourceName}/${this.id}/head`
        }).then((resp) => {
            this.set(resp);
            this.trigger('g:specHead', resp);
            return resp;
        }).fail((err) => {
            this.trigger('g:error', err);
        });
    }
});

export default DataflowModel;
