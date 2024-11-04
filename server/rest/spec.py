from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, filtermodel
from girder.constants import AccessType

from ..models.dataflow import Dataflow
from ..models.spec import Spec as SpecModel


class Spec(Resource):
    """Spec resource."""

    def __init__(self):
        super(Spec, self).__init__()
        self.resourceName = "spec"
        self._model = SpecModel()
        self.route("GET", (), self.listSpecs)
        self.route("GET", (":id",), self.getSpec)
        self.route("POST", (), self.createSpec)
        self.route("DELETE", (":id",), self.deleteSpec)

    @access.public
    @autoDescribeRoute(
        Description("List all available Specs for a given Dataflow")
        .param("dataflowId", "The ID of the Dataflow", required=True)
        .pagingParams(defaultSort="name")
    )
    @filtermodel(model="spec", plugin="dataflows")
    def listSpecs(self, limit, offset, sort, params):
        dataflow = Dataflow().load(
            id=params["dataflowId"],
            user=self.getCurrentUser(),
            level=AccessType.READ,
            exc=True,
        )

        return Dataflow().childSpecs(
            dataflow=dataflow, limit=limit, offset=offset, sort=sort, filters={}
        )

    @access.public
    @autoDescribeRoute(
        Description("Get a Spec by ID").modelParam(
            "id", model=SpecModel, level=AccessType.READ
        )
    )
    @filtermodel(model="spec", plugin="dataflows")
    def getSpec(self, spec):
        return spec

    @access.user
    @autoDescribeRoute(
        Description("Create a new Spec")
        .modelParam(
            "dataflowId", model=Dataflow, level=AccessType.WRITE, paramType="query"
        )
        .jsonParam("data", "The Spec to create", paramType="body", requireObject=True)
        .errorResponse()
        .errorResponse("Write access was denied on the parent Dataflow.", 403)
    )
    @filtermodel(model="spec", plugin="dataflows")
    def createSpec(self, dataflow, data):
        return self._model.createSpec(dataflow, data, self.getCurrentUser())

    @access.user
    @autoDescribeRoute(
        Description("Delete a Spec by ID")
        .modelParam("id", model=SpecModel, level=AccessType.WRITE)
        .errorResponse()
        .errorResponse("Write access was denied on the Spec.", 403)
    )
    def deleteSpec(self, spec):
        self._model.remove(spec)
