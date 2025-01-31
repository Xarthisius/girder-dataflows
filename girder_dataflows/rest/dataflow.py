from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, filtermodel
from girder.constants import AccessType
from girder.exceptions import ValidationException
from girder.models.folder import Folder
from girder.models.setting import Setting

from ..constants import PluginSettings
from ..models.dataflow import Dataflow as DataflowModel
from ..models.spec import Spec


class Dataflow(Resource):
    """Dataflow resource."""

    def __init__(self):
        super(Dataflow, self).__init__()
        self.resourceName = "dataflow"
        self._model = DataflowModel()
        self.route("GET", (), self.listDataflows)
        self.route("GET", (":id",), self.getDataflow)
        self.route("PUT", (":id",), self.updateDataflow)
        self.route("PUT", (":id", "execute"), self.executeDataflow)
        self.route("DELETE", (":id",), self.deleteDataflow)
        self.route("POST", (), self.createDataflow)
        self.route("GET", ("images",), self.dataflowImages)

    @access.public
    @autoDescribeRoute(
        Description("List all available Dataflows that can be executed.").pagingParams(
            defaultSort="name"
        )
    )
    @filtermodel(model="dataflow", plugin="dataflows")
    def listDataflows(self, limit, offset, sort, params):
        return list(
            self._model.listDataflows(
                query=None,
                offset=offset,
                limit=limit,
                user=self.getCurrentUser(),
                sort=sort,
                level=AccessType.READ,
            )
        )

    @access.user
    @autoDescribeRoute(
        Description("Get a Dataflow by ID.")
        .modelParam("id", model=DataflowModel, level=AccessType.READ)
        .errorResponse("ID was invalid.")
        .errorResponse("Read access was denied for the Dataflow.", 403)
    )
    @filtermodel(model="dataflow", plugin="dataflows")
    def getDataflow(self, dataflow):
        dataflow["spec"] = self._model.currentSpec(dataflow)
        dataflow["status"] = self._model.currentStatus(dataflow)
        return dataflow

    @access.user
    @autoDescribeRoute(
        Description("Create a new Dataflow.")
        .param("name", "Name of the Dataflow.", required=True)
        .param("description", "Description of the Dataflow.", required=False)
        .jsonParam("spec", "Specification of the Dataflow.")
    )
    @filtermodel(model="dataflow", plugin="dataflows")
    def createDataflow(self, name, description, spec):
        if not name:
            raise ValidationException("Dataflow name must not be empty.", "name")
        # validate the dataflow spec
        spec = self._validateDataflow(spec)

        # create the dataflow item
        dataflow = self._model.createDataflow(
            name,
            description,
            self.getCurrentUser(),
        )

        # create the dataflow spec item
        Spec().createSpec(dataflow, spec)

        # return the dataflow item
        return dataflow

    @access.user
    @autoDescribeRoute(
        Description("Start or stop a Dataflow.")
        .modelParam("id", model=DataflowModel, level=AccessType.WRITE)
        .param("action", "Action to perform on the Dataflow.", enum=["start", "stop"])
    )
    @filtermodel(model="dataflow", plugin="dataflows")
    def executeDataflow(self, dataflow, action):
        dataflow["spec"] = self._model.currentSpec(dataflow)
        if action == "start":
            # start the dataflow
            self._model.createService(dataflow, self.getCurrentUser())
        elif action == "stop":
            # stop the dataflow
            self._model.removeService(dataflow)
        dataflow["status"] = self._model.currentStatus(dataflow)
        return dataflow

    @access.user
    @autoDescribeRoute(
        Description("Get the status of a Dataflow.").modelParam(
            "id", model=DataflowModel, level=AccessType.READ
        )
    )
    def getDataflowStatus(self, item):
        # get the dataflow status
        pass

    @access.user
    @autoDescribeRoute(
        Description("Update a Dataflow.")
        .modelParam("id", model=DataflowModel, level=AccessType.WRITE)
        .param("name", "Name of the Dataflow.")
        .param("description", "Description of the Dataflow.")
    )
    @filtermodel(model="dataflow", plugin="dataflows")
    def updateDataflow(self, dataflow, name, description):
        return self._model.updateDataflow(
            dataflow,
            name,
            description,
        )

    def _validateDataflow(self, spec):
        Folder().load(spec.get("destinationId"), force=True, exc=True)
        if spec["type"] == "openmsi" and not spec.get("topic"):
            raise ValidationException("Dataflow spec must contain a topic.", "spec")

        if not spec.get("image"):
            raise ValidationException("Dataflow spec must contain an image.", "spec")
        return spec

    @access.public
    @autoDescribeRoute(Description("Get available Dataflow images."))
    def dataflowImages(self):
        return Setting().get(PluginSettings.DOCKER_IMAGES) or []

    @access.user
    @autoDescribeRoute(
        Description("Delete a Dataflow.")
        .modelParam("id", model=DataflowModel, level=AccessType.WRITE)
        .errorResponse("ID was invalid.")
        .errorResponse("Admin access was denied for the Dataflow.", 403)
    )
    def deleteDataflow(self, dataflow):
        if self._model.currentStatus(dataflow):
            raise ValidationException(
                "Dataflow must be stopped before it can be deleted.", "id"
            )
        Spec().removeWithQuery({"dataflowId": dataflow["_id"]})
        self._model.remove(dataflow)
