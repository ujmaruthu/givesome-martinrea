# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

#: The Shuup default registration form for person
#: This overrides the setting from `registration` lib
#: to allow custom logic like receiving the request from kwargs
REGISTRATION_FORM = "shuup.front.apps.registration.forms.PersonRegistrationForm"
