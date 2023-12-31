# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
#: Require email-based activation for users?
#:
#: Configures the content subtype of the emails sent by Auth app
#: Set `html` if your template is HTML-based
#:
SHUUP_AUTH_EMAIL_CONTENT_SUBTYPE = "plain"


#: Specify the authentication form to be used in login views
#:
SHUUP_AUTH_LOGIN_FORM_SPEC = "shuup.front.apps.auth.forms.EmailAuthenticationForm"
