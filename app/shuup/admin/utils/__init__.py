# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


def media_folder_from_folder(folder):
    """
    Gets media folder from folder

    :param Folder: the folder you want to get the media folder from

    :rtype: shuup.MediaFolder
    """

    return folder.media_folder.first()
