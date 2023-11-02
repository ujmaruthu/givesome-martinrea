# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import os


def get_sample_file_content(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(path):
        from six import BytesIO

        return BytesIO(open(path, "rb").read())
