# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from givesome.front.views.givecard_wallet import bump_wallet_cache, ensure_session_wallet
from givesome.models import Givecard, GivecardBatch, GivecardCampaign


def find_givecard_by_code(code: str) -> Optional[Givecard]:
    """
    Try to find a Multicard or Givecard with given code
    For Multicards, best multicard for redeeming is returned
    """
    givecard = None
    # Search code from Multicards first
    batch = GivecardBatch.objects.redeemable().filter(code=code)
    if batch.exists():
        givecard = batch.first().get_best_multicard()

    # Search code from Unique Givecards
    if givecard is None:
        givecard = Givecard.objects.redeemable().filter(code=code).first()
    return givecard


def add_givecard_to_wallet(givecard: Givecard, request) -> dict:
    givecard_data = givecard.get_data_for_wallet()
    wallet = ensure_session_wallet(request)
    wallet[givecard_data["code"]] = givecard_data
    request.session.modified = True
    return givecard_data


class GivecardRedeemView(View):
    @staticmethod
    def _is_givecard_in_wallet(code: str, request) -> bool:
        """Check if given code is already in wallet"""
        wallet = ensure_session_wallet(request)
        return code in wallet

    @staticmethod
    def _get_givecard_next_url(givecard: Givecard) -> str:
        """Link shown on redemption successful modal"""
        if givecard.batch.redirect_office is not None:
            return reverse("office", kwargs={"pk": givecard.batch.redirect_office.pk})
        elif givecard.batch.office is not None:
            return reverse("office", kwargs={"pk": givecard.batch.office.pk})
        elif givecard.batch.supplier is not None:
            return reverse("shuup:supplier", kwargs={"slug": givecard.batch.supplier.slug})
        return "/"

    @staticmethod
    def _get_campaign_data(campaign: GivecardCampaign) -> dict:
        """Campaign information shown on redemption successful modal"""
        campaign_data = {
            "campaign_name": campaign.name,
            "campaign_message": campaign.message,
            "campaign_supplier_name": campaign.supplier.name if campaign.supplier is not None else "Givesome",
        }
        if hasattr(campaign, "image"):
            campaign_image_url = f"{settings.MEDIA_URL}{campaign.get_image_thumbnail(size=(400, 400))}"
            campaign_data["campaign_image"] = campaign_image_url
        return campaign_data

    def post(self, request, *args, **kwargs) -> JsonResponse:
        user = request.user
        code = request.POST.get("givecard_code")

        if code is None:
            return JsonResponse({"error": _("Error getting Givecard PIN!")}, status=400)

        if self._is_givecard_in_wallet(code, request):
            return JsonResponse({"error": _("You have already redeemed this PIN")}, status=400)

        givecard = find_givecard_by_code(code)

        if givecard is None:
            return JsonResponse({"error": _("This PIN is not recognized or has expired")}, status=400)

        # Claim Givecard for user
        redeeming_user = user if user.is_authenticated else None
        try:
            givecard.redeem(user=redeeming_user)
        except ValidationError:
            # If redemption error was caused by a error that user can know, display that error
            for error in givecard.get_redemption_errors(redeeming_user):
                if error.code == "visible_for_user":
                    return JsonResponse({"error": error.message}, status=400)
            # Else display default error message
            return JsonResponse({"error": _("Error redeeming Givecard!")}, status=400)

        # Add givecard to session storage and cache wallet
        givecard_data = add_givecard_to_wallet(givecard, request)
        bump_wallet_cache(request)  # Clear cache, it's populated again on next page load
        givecard_data["code"] = code

        # Get extra data
        campaign_data = self._get_campaign_data(givecard.batch.campaign)
        next_url = self._get_givecard_next_url(givecard)

        return JsonResponse(
            {
                "next_url": next_url,
                **givecard_data,
                **campaign_data,
            }
        )
