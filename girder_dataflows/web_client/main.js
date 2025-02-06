// Extends and overrides API
import './routes';

const { wrap } = girder.utilities.PluginUtils;
const GlobalNavView = girder.views.layout.GlobalNavView;

// Add a new global nav item for creating and browsing workflows
wrap(GlobalNavView, 'initialize', function (initialize) {
    initialize.apply(this, arguments);

    this.defaultNavItems.push({
        name: 'DataFlows',
        icon: 'icon-cubes',
        target: 'dataflows'
    });
});
