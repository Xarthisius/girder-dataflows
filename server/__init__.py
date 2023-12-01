#!/usr/bin/env python
# -*- coding: utf-8 -*-


from .rest.dataflow import Dataflow
from .rest.spec import Spec


def load(info):
    info["apiRoot"].dataflow = Dataflow()
    info["apiRoot"].spec = Spec()
