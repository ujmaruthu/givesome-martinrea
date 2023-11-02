#!/usr/bin/env python
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


class RemovedInShuup20Warning(PendingDeprecationWarning):
    pass


class RemovedFromShuupWarning(DeprecationWarning):
    pass


RemovedInFutureShuupWarning = RemovedInShuup20Warning
