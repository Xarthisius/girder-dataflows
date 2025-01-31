"""
Dagster Workspace handler.
"""

import yaml


class DagsterWorkspace:
    """
    Dagster Workspace handler.

    Given a file 'workspace.yaml' with the following content:

       load_from:
       - grpc_server:
           host: dagster_example
           port: 4000
           location_name: "girder_user_code"

    1) loads the workspace object from the file
    2) saves the workspace object to a file
    3) removes grpc_server from the workspace object based on location_name
    4) adds grpc_server to the workspace object
    """

    def __init__(self, workspace_file):
        self.workspace_file = workspace_file
        self.workspace = yaml.safe_load(open(workspace_file, "r"))

    def save(self):
        """Save the workspace object to a file."""
        yaml.safe_dump(self.workspace, open(self.workspace_file, "w"))

    def remove_location(self, location_name):
        """Remove grpc_server from the workspace object based on location_name."""
        for i, location in enumerate(self.workspace["load_from"]):
            if location.get("grpc_server", {}).get("location_name") == location_name:
                self.workspace["load_from"].pop(i)
                break

    def add_location(self, location_name, host, port=4000):
        """Add grpc_server to the workspace object."""
        location = {
            "grpc_server": {
                "host": host,
                "port": port,
                "location_name": location_name,
            }
        }
        self.workspace["load_from"].append(location)
