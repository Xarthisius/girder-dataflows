import Collection from 'girder/collections/Collection';

import DataflowModel from '../models/DataflowModel';

var DataflowCollection = Collection.extend({
    resourceName: 'dataflow',
    model: DataflowModel,
    pageLimit: 100
});

export default DataflowCollection;
