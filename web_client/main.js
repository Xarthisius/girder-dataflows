// Extends and overrides API
import { wrap } from 'girder/utilities/PluginUtils';
import GlobalNavView from 'girder/views/layout/GlobalNavView';
import FileListWidget from 'girder/views/widgets/FileListWidget';
import { SORT_DESC } from 'girder/constants';

import './routes';

// Add a new global nav item for creating and browsing workflows
wrap(GlobalNavView, 'initialize', function (initialize) {
    initialize.apply(this, arguments);

    this.defaultNavItems.push({
        name: 'DataFlows',
        icon: 'icon-cubes',
        target: 'dataflows'
    });
});
