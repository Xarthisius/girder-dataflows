import datetime
from girder.constants import AccessType
from girder.models.model_base import AccessControlledModel
from girder.models.user import User


class Spec(AccessControlledModel):
    """
    This model represents Dataflow specification.
    """

    def initialize(self):
        self.name = "spec"
        self.ensureIndices(("dataflowId", "created"))

        self.resourceColl = "dataflow"
        self.resourceParent = "dataflowId"

        self.exposeFields(
            level=AccessType.READ,
            fields=("_id", "created", "creatorId", "type", "dataflowId", "spec"),
        )

    def validate(self, doc):
        return doc

    def createSpec(self, dataflow, spec, creator=None, save=True):
        """
        Create a new spec for a dataflow.
        """
        if creator is None:
            creator = User().load(dataflow["creatorId"], force=True)

        doc = {
            "creatorId": creator["_id"],
            "created": datetime.datetime.utcnow(),
            "dataflowId": dataflow["_id"],
            "type": dataflow["type"],
            "spec": spec,
        }
        self.setUserAccess(doc, user=creator, level=AccessType.ADMIN, save=False)

        if save:
            return self.save(doc)
        return doc
