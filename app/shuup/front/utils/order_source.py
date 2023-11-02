# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from typing import Iterable, Union

from shuup.apps.provides import get_provide_objects
from shuup.core.models import OrderLine
from shuup.core.order_creator import SourceLine


class LineProperty:
    name = None
    value = None

    def __init__(self, name, value):
        self.name = name
        self.value = value


class BaseLinePropertiesDescriptor:
    @classmethod
    def get_line_properties(cls, line: Union[OrderLine, SourceLine], **kwargs) -> Iterable[LineProperty]:
        raise NotImplementedError()


def get_line_properties(line: Union[OrderLine, SourceLine]) -> Iterable[LineProperty]:
    line_properties_descriptors = get_provide_objects("front_line_properties_descriptor")

    for line_properties_descriptor in line_properties_descriptors:  # type: Iterable[BaseLinePropertiesDescriptor]
        if not issubclass(line_properties_descriptor, BaseLinePropertiesDescriptor):
            return

        yield from line_properties_descriptor.get_line_properties(line)
