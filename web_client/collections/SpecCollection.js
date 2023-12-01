import Collection from 'girder/collections/Collection';

import SpecModel from '../models/SpecModel';

var SpecCollection = Collection.extend({
    resourceName: 'spec',
    model: SpecModel,
    pageLimit: 100
});

export default SpecCollection;
