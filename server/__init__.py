#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.constants import AccessType, SettingDefault
from girder.models.file import File
from girder.utility import setting_utilities

from .constants import PluginSettings
from .rest.dataflow import Dataflow
from .rest.spec import Spec


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
    }
)
def validateOtherSettings(event):
    pass


def load(info):
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
        }
    )
    info["apiRoot"].dataflow = Dataflow()
    info["apiRoot"].spec = Spec()

    File().exposeFields(level=AccessType.READ, fields="sha512")
