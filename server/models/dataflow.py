import datetime
import json
from girder.api.rest import getApiUrl
from girder.constants import AccessType, SortDir
from girder.models.api_key import ApiKey
from girder.models.model_base import AccessControlledModel, ValidationException

from ..lib.service import DataflowService
from .spec import Spec


class Dataflow(AccessControlledModel):
    """
    This model represents a dataflow, which is a set of name, description and a spec model.
    """

    def initialize(self):
        self.name = "dataflow"
        self.ensureIndices(("name", "description", "creatorId"))
        self.exposeFields(
            level=AccessType.READ,
            fields=(
                "_id",
                "name",
                "description",
                "creatorId",
                "created",
                "updated",
                "public",
                "publicFlags",
                "spec",
                "status",
                "type",
            ),
        )

    def validate(self, doc):
        """
        Validate the dataflow schema.
        """
        if not doc:
            raise ValidationException("Dataflow document is empty.")
        return doc

    def createDataflow(self, name, description, creator, public=None):
        """
        Create a new dataflow.
        """
        dataflow = {
            "name": name,
            "description": description,
            "creatorId": creator["_id"],
            "type": "dataflow",
            "status": None,
        }
        self.setUserAccess(dataflow, user=creator, level=AccessType.ADMIN, save=False)
        if public is not None and isinstance(public, bool):
            self.setPublic(dataflow, public, save=False)
        return self.save(dataflow)

    def updateDataflow(
        self, dataflow, name, description, status=None, dataflow_type="dataflow"
    ):
        """
        Update an existing dataflow.
        """
        dataflow["name"] = name
        dataflow["description"] = description
        dataflow["updated"] = datetime.datetime.utcnow()
        dataflow["status"] = status or self.currentStatus(dataflow)
        if dataflow_type:
            dataflow["type"] = dataflow_type
        return self.save(dataflow)

    def removeDataflow(self, dataflow):
        """
        Remove a dataflow.
        """
        self.remove(dataflow)

    def listDataflows(
        self,
        query=None,
        offset=0,
        limit=0,
        timeout=None,
        fields=None,
        sort=None,
        user=None,
        level=AccessType.READ,
        types=None,
        statuses=None,
        **kwargs,
    ):
        if not query:
            query = {}

        return super(Dataflow, self).findWithPermissions(
            query,
            offset=offset,
            limit=limit,
            timeout=timeout,
            fields=fields,
            sort=sort,
            user=user,
            level=level,
            **kwargs,
        )

    def childSpecs(
        self,
        dataflow,
        limit=0,
        offset=0,
        sort=None,
        filters=None,
        user=None,
        level=AccessType.READ,
        **kwargs,
    ):
        """
        Return a list of all specs within the dataflow.
        """
        q = {"dataflowId": dataflow["_id"]}
        q.update(filters or {})

        return list(
            Spec().find(
                q,
                offset=offset,
                limit=limit,
                sort=sort,
            )
        )

    def currentSpec(self, dataflow):
        """
        Return the current spec for the dataflow.
        """
        if spec := Spec().findOne(
            {"dataflowId": dataflow["_id"]}, sort=[("created", SortDir.DESCENDING)]
        ):
            return spec["spec"]

    def createService(self, dataflow, user):
        """
        Create a new service for the dataflow.
        """
        spec = Spec().findOne(
            {"dataflowId": dataflow["_id"]}, sort=[("created", SortDir.DESCENDING)]
        )
        service = DataflowService()

        meta = {"dataflow": str(dataflow["_id"]), "spec": str(spec["_id"])}
        spec = spec["spec"]

        cmd = (
            "GirderUploadStreamProcessor "
            "--config /app/test.config "
            f"--topic_name {spec['topic']} "
            f"--girder_root_folder_id {spec['destinationId']} "
            f"--metadata \'{json.dumps(meta)}\' "
            f"{getApiUrl(preferReferer=True)} "
            f"{self._getApiKey(user)}"
        )

        service.create(
            image=spec["image"],
            name=f"flow-{dataflow['_id']}",
            command=cmd,
            workdir="/tmp",
            networks=["host"],
        )
        # self.update({"_id": dataflow["_id"]}, {"$set": {"status": self.currentStatus(dataflow)}})
        return service

    def removeService(self, dataflow):
        """
        Remove the service for the dataflow.
        """
        service = DataflowService(f"flow-{dataflow['_id']}")
        service.remove()
        # self.update({"_id": dataflow["_id"]}, {"$set": {"status": None}})
        return service

    def currentStatus(self, dataflow):
        """
        Inspect the service for the dataflow.
        """
        if service := DataflowService(f"flow-{dataflow['_id']}").get():
            task = service.tasks()[0]
            return task["Status"]

    @staticmethod
    def _getApiKey(user):
        """
        Get the API key for the user.
        """
        apikey = ApiKey().findOne({"userId": user["_id"], "name": "Dataflows"})
        if not apikey:
            apikey = ApiKey().createApiKey(user, name="Dataflows")
        return apikey["key"]
