import docker


class DataflowService(object):
    """
    Provides a wrapper around Docker Swarm Services.
    """

    def __init__(self, service_id=None):
        self.client = docker.from_env()
        try:
            self.service = self.client.services.get(service_id)
        except (docker.errors.NotFound, docker.errors.NullResource):
            self.service = None

    def create(self, **kwargs):
        """
        Create the service.
        """
        service = self.client.services.create(**kwargs)
        self.service = service
        return service

    def get(self):
        """
        Get the service details.
        """
        if self.service:
            return self.client.services.get(self.service.id)

    def logs(self, **kwargs):
        """
        Get the service logs.
        """
        return self.service.logs(stdout=True, **kwargs)

    def remove(self):
        """
        Remove the service.
        """
        return self.service.remove()

    def restart(self):
        """
        Restart the service.
        """
        return self.service.force_update()


if __name__ == '__main__':
    service = DataflowService()
    print(service.create(image="redis:7-bullseye", name="dataflow-1", command="/bin/sleep infinity"))
    print(service.logs())
