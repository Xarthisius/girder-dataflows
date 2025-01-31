#!/usr/bin/env python
# -*- coding: utf-8 -*-


class PluginSettings:
    KAFKA_BOOTSTRAP_SERVERS = "dataflows.kafka_bootstrap_servers"
    KAFKA_SASL_MECHANISM = "dataflows.kafka_sasl_mechanism"
    KAFKA_SASL_USERNAME = "dataflows.kafka_sasl_username"
    KAFKA_SASL_PASSWORD = "dataflows.kafka_sasl_password"
    KAFKA_SECURITY_PROTOCOL = "dataflows.kafka_security_protocol"
    DAGSTER_POSTGRES_USER = "dataflows.dagster_postgres_user"
    DAGSTER_POSTGRES_PASSWORD = "dataflows.dagster_postgres_password"
    DAGSTER_POSTGRES_DB = "dataflows.dagster_postgres_db"
    DOCKER_IMAGES = "dataflows.docker_images"
