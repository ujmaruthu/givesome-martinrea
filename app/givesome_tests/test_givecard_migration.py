# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import pytest
from django.core.management import get_commands, load_command_class
from django.utils import timezone

vendor0 = "Vendor0"
vendor1 = "Vendor1"
campaign_key0 = "campaign0"
campaign_key1 = "campaign1"


unimportable = {
    "givecards": {
        "PNCGKS": {
            # Unredeemed and expired
            "entity": campaign_key0,
            "expires": 1599077188,
            "redeemed": False,
            "value": 5,
        },
        "PNKMRT": {
            # Redeemed and spent
            "entity": campaign_key1,
            "expires": 1547856000,
            "redeemed": True,
            "redeemed-by": "kbcgyhYQOab3rwYeSG818xlQ5wH3",
            "redeemed-date": 1544798023,
            "value": 5,
        },
        "ALEXTE": {
            # Unexpired multicard that has been used all the way up.
            "entity": campaign_key0,
            "expires": timezone.now().timestamp() + 300000,
            "multi-use": True,
            "redeemed-group": {
                "-MUid4ZAN9WtYQL4VeDm": {"redeemed-by": "pLWxFPz7gXRWqpfPGFJ0jLEqkvo1", "redeemed-date": 1614616484},
            },
            "redeemed-group-list": {"pLWxFPz7gXRWqpfPGFJ0jLEqkvo1": True},
            "skin": "-LntZ5ord2JDYhPdj72d",
            "use-count": 1,
            "value": 2,
        },
        "ROTARY": {
            # Completely unredeemed multicard, expired
            "entity": campaign_key0,
            "expires": 1599077188,
            "multi-use": True,
            "use-count": 291,
            "value": 2,
        },
    },
    "users": {
        "kbcgyhYQOab3rwYeSG818xlQ5wH3": {
            "accounts": {
                "givecards": {
                    "PNKMRT": {"date-redeemed": 1544798023, "entity": "campaign", "original-value": 5, "value": 0}
                }
            }
        },
        "pLWxFPz7gXRWqpfPGFJ0jLEqkvo1": {
            "accounts": {
                "givecards": {
                    "ALEXTE": {"date-redeemed": 1544798023, "entity": "campaign", "original-value": 2, "value": 0}
                }
            }
        },
    },
}

importable = {
    "givecards": {
        "cards": {
            "PNCGKS": {
                # Unredeemed and not expired
                "entity": campaign_key0,
                "expires": int(timezone.now().timestamp()) + 400000,  # several days from now
                "redeemed": False,
                "value": 5,
            },
            # Expired, but redeemed and unspent
            "PNKMRT": {
                "entity": campaign_key1,
                "expires": 1547856000,
                "redeemed": True,
                "redeemed-by": "kbcgyhYQOab3rwYeSG818xlQ5wH3",
                "redeemed-date": 1544798023,
                "value": 5,
            },
            "ROTARY": {
                # Unredeemed multicard not expired
                "entity": campaign_key0,
                "expires": int(timezone.now().timestamp()) + 300000,
                "multi-use": True,
                "use-count": 5,
                "value": 2,
            },
            "ALEXTE": {
                # Redeemed multicard that still has some uses left, not expired
                "entity": campaign_key0,
                "expires": int(timezone.now().timestamp()) + 300000,
                "multi-use": True,
                "redeemed-group": {
                    "-MUid4ZAN9WtYQL4VeDm": {
                        "redeemed-by": "pLWxFPz7gXRWqpfPGFJ0jLEqkvo1",
                        "redeemed-date": 1614616484,
                    },
                },
                "redeemed-group-list": {"pLWxFPz7gXRWqpfPGFJ0jLEqkvo1": True},
                "skin": "-LntZ5ord2JDYhPdj72d",
                "use-count": 5,
                "value": 2,
            },
        },
        "entities": {
            campaign_key0: {"message": "campaign", "name": vendor0},
            campaign_key1: {"message": "eq3", "name": vendor1},
        },
    },
    "users": {
        "kbcgyhYQOab3rwYeSG818xlQ5wH3": {
            "accounts": {
                "givecards": {
                    "PNKMRT": {"date-redeemed": 1544798023, "entity": "campaign", "original-value": 5, "value": 5}
                }
            }
        },
        "pLWxFPz7gXRWqpfPGFJ0jLEqkvo1": {
            "accounts": {
                "givecards": {
                    "ALEXTE": {"date-redeemed": 1544798023, "entity": "campaign", "original-value": 2, "value": 0}
                }
            }
        },
    },
}


def _get_command(name):
    app_name = get_commands()[name]
    return load_command_class(app_name, name)


@pytest.mark.django_db
def test_card_is_importable():
    cmd = _get_command("migrate_givesome_data")

    cmd.givesome_data = unimportable
    assert not cmd._card_is_importable(cmd.givesome_data["givecards"]["PNCGKS"], "PNCGKS")
    assert not cmd._card_is_importable(cmd.givesome_data["givecards"]["PNKMRT"], "PNKMRT")
    assert not cmd._card_is_importable(cmd.givesome_data["givecards"]["ALEXTE"], "ALEXTE")
    assert not cmd._card_is_importable(cmd.givesome_data["givecards"]["ROTARY"], "PNCGKS")

    cmd.givesome_data = importable
    assert cmd._card_is_importable(cmd.givesome_data["givecards"]["cards"]["PNCGKS"], "PNCGKS")
    assert cmd._card_is_importable(cmd.givesome_data["givecards"]["cards"]["PNKMRT"], "PNKMRT")
    assert cmd._card_is_importable(cmd.givesome_data["givecards"]["cards"]["ALEXTE"], "ALEXTE")
    assert cmd._card_is_importable(cmd.givesome_data["givecards"]["cards"]["ROTARY"], "PNCGKS")
