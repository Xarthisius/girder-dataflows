import DataflowModel from '../models/DataflowModel';

const Collection = girder.collections.Collection;

var DataflowCollection = Collection.extend({
    resourceName: 'dataflow',
    model: DataflowModel,
    pageLimit: 100
});

export default DataflowCollection;
