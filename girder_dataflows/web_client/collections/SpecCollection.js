import SpecModel from '../models/SpecModel';

const Collection = girder.collections.Collection;

var SpecCollection = Collection.extend({
    resourceName: 'spec',
    model: SpecModel,
    pageLimit: 100
});

export default SpecCollection;
