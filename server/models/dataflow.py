import datetime
import json
import os
from girder.api.rest import getApiUrl
from girder.constants import AccessType, SortDir
from girder.models.api_key import ApiKey
from girder.models.model_base import AccessControlledModel, ValidationException
from girder.models.setting import Setting

from ..constants import PluginSettings
from ..lib.dagster_workspace import DagsterWorkspace
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

    def createDataflow(
        self, name, description, creator, dataflow_type="openmsi", public=None
    ):
        """
        Create a new dataflow.
        """
        dataflow = {
            "name": name,
            "description": description,
            "creatorId": creator["_id"],
            "type": dataflow_type,
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
        if dataflow["spec"]["type"] == "openmsi":
            return self.createOpenMSIService(dataflow, user)
        elif dataflow["spec"]["type"] == "dagster":
            return self.createDagsterService(dataflow, user)

    def createDagsterService(self, dataflow, user):
        """
        Create a new Dagster service for the dataflow.
        """
        spec = Spec().findOne(
            {"dataflowId": dataflow["_id"]}, sort=[("created", SortDir.DESCENDING)]
        )
        service = DataflowService()

        spec_id = spec["_id"]
        spec = spec["spec"]

        env = [
            f"GIRDER_API_URL={getApiUrl(preferReferer=True)}",
            f"GIRDER_API_KEY={self._getApiKey(user, token=False)}",
            f"GIRDER_TOKEN={self._getApiKey(user, token=True)}",
            f"DAGSTER_CURRENT_IMAGE={spec['image']}",
            f"DATAFLOW_ID={dataflow['_id']}",
            f"DATAFLOW_SPEC_ID={spec_id}",
            f"DATAFLOW_SRC_FOLDER_ID={spec['sourceId']}",
            f"DATAFLOW_DST_FOLDER_ID={spec['destinationId']}",
            f"DAGSTER_POSTGRES_DB={Setting().get(PluginSettings.DAGSTER_POSTGRES_DB)}",
            f"DAGSTER_POSTGRES_USER={Setting().get(PluginSettings.DAGSTER_POSTGRES_USER)}",
            f"DAGSTER_POSTGRES_PASSWORD={Setting().get(PluginSettings.DAGSTER_POSTGRES_PASSWORD)}",
        ]
        container_context = {
            "docker": {
                "env_vars": env,
                "container_kwargs": {
                    "extra_hosts": {"girder.local.xarthisius.xyz": "host-gateway"}
                },
            }
        }
        extra = f"DAGSTER_CLI_API_GRPC_CONTAINER_CONTEXT={json.dumps(container_context)}"
        env.append(extra)

        hosts = {}
        if os.environ.get("DOMAIN") == "local.xarthisius.xyz":
            hosts["girder.local.xarthisius.xyz"] = "host-gateway"

        name = f"flow-{dataflow['_id']}"
        service.create(
            name=name,
            image=spec["image"],
            env=env,
            networks=["wt_dagster"],
            hosts=hosts,
        )
        self._updateDagsterWorkspace(name, name)

    def _updateDagsterWorkspace(self, location, host, increment=1):
        """
        Update the Dagster workspace.
        """
        workspace = DagsterWorkspace("/girder/workspace.yaml")
        if increment > 0:
            workspace.add_location(location, host)
        else:
            workspace.remove_location(location)
        workspace.save()
        # This is obnoxious, but we need to restart the dagster services
        # for service_name in ("wt_dagster_web", "wt_dagster_daemon"):
        #    service = DataflowService(service_name)
        #    service.restart()

    def createOpenMSIService(self, dataflow, user):
        """
        Create a new OpenMSI service for the dataflow.
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
            f"--metadata '{json.dumps(meta)}' "
            f"{getApiUrl(preferReferer=True)} "
            f"{self._getApiKey(user)}"
        )

        env = [
            f"BROKER_BOOTSTRAP_SERVERS={Setting().get(PluginSettings.KAFKA_BOOTSTRAP_SERVERS)}",
            f"BROKER_SASL_MECHANISM={Setting().get(PluginSettings.KAFKA_SASL_MECHANISM)}",
            f"BROKER_SECURITY_PROTOCOL={Setting().get(PluginSettings.KAFKA_SECURITY_PROTOCOL)}",
            f"BROKER_SASL_USERNAME={Setting().get(PluginSettings.KAFKA_SASL_USERNAME)}",
            f"BROKER_SASL_PASSWORD={Setting().get(PluginSettings.KAFKA_SASL_PASSWORD)}",
        ]

        service.create(
            image=spec["image"],
            name=f"flow-{dataflow['_id']}",
            command=cmd,
            env=env,
            workdir="/tmp",
            networks=["host"],
        )
        # self.update({"_id": dataflow["_id"]}, {"$set": {"status": self.currentStatus(dataflow)}})
        return service

    def removeService(self, dataflow):
        """
        Remove the service for the dataflow.
        """
        name = f"flow-{dataflow['_id']}"
        service = DataflowService(name)
        service.remove()
        if dataflow["spec"]["type"] == "dagster":
            self._updateDagsterWorkspace(name, name, increment=-1)
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
    def _getApiKey(user, token=False):
        """
        Get the API key for the user.
        """
        apikey = ApiKey().findOne({"userId": user["_id"], "name": "Dataflows"})
        if not apikey:
            apikey = ApiKey().createApiKey(user, name="Dataflows")
        if token:
            _, girder_token = ApiKey().createToken(apikey["key"])
            return girder_token["_id"]
        return apikey["key"]
