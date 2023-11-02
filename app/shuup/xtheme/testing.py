# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.utils import update_module_attributes

from ._theme import override_current_theme_class

__all__ = [
    "override_current_theme_class",
]

update_module_attributes(__all__, __name__)
