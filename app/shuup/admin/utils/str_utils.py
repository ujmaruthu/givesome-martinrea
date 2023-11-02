# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import re


def camelcase_to_snakecase(string_to_convert):
    """
    Convert CamelCase string to snake_case

    Original solution in
    http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string_to_convert)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
