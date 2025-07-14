#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
from girder.plugin import GirderPlugin, registerPluginStaticContent
from girder.utility.model_importer import ModelImporter
from girder.constants import AccessType
from girder.settings import SettingDefault
from girder.models.file import File
from girder.utility import setting_utilities

from .constants import PluginSettings
from .rest.dataflow import Dataflow
from .rest.spec import Spec
from .models.dataflow import Dataflow as DataflowModel
from .models.spec import Spec as SpecModel


@setting_utilities.validator(
    {
        PluginSettings.KAFKA_BOOTSTRAP_SERVERS,
        PluginSettings.KAFKA_SASL_MECHANISM,
        PluginSettings.KAFKA_SASL_USERNAME,
        PluginSettings.KAFKA_SASL_PASSWORD,
        PluginSettings.KAFKA_SECURITY_PROTOCOL,
        PluginSettings.DAGSTER_POSTGRES_USER,
        PluginSettings.DAGSTER_POSTGRES_PASSWORD,
        PluginSettings.DAGSTER_POSTGRES_DB,
        PluginSettings.DOCKER_IMAGES,
    }
)
def validateOtherSettings(event):
    pass


class DataflowsPlugin(GirderPlugin):
    DISPLAY_NAME = "Dataflows"

    def load(self, info):
        ModelImporter.registerModel("dataflow", DataflowModel, plugin="dataflows")
        ModelImporter.registerModel("spec", SpecModel, plugin="dataflows")
        SettingDefault.defaults.update(
            {
                PluginSettings.KAFKA_BOOTSTRAP_SERVERS: "localhost:9092",
                PluginSettings.KAFKA_SASL_MECHANISM: "PLAIN",
                PluginSettings.KAFKA_SASL_USERNAME: "admin",
                PluginSettings.KAFKA_SASL_PASSWORD: "admin-secret",
                PluginSettings.KAFKA_SECURITY_PROTOCOL: "SASL_PLAINTEXT",
                PluginSettings.DAGSTER_POSTGRES_USER: "postgres_user",
                PluginSettings.DAGSTER_POSTGRES_PASSWORD: "postgres_password",
                PluginSettings.DAGSTER_POSTGRES_DB: "postgres_db",
                PluginSettings.DOCKER_IMAGES: [
                    "xarthisius/openmsistream:demo",
                    "xarthisius/dagster_example:demo",
                    "xarthisius/dagster_example:latest",
                ],
            }
        )
        info["apiRoot"].dataflow = Dataflow()
        info["apiRoot"].spec = Spec()

        File().exposeFields(level=AccessType.READ, fields="sha512")
        registerPluginStaticContent(
            plugin="dataflows",
            css=["/style.css"],
            js=["/girder-plugin-dataflows.umd.cjs"],
            staticDir=Path(__file__).parent / "web_client" / "dist",
            tree=info["serverRoot"],
        )
