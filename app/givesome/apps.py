# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "givesome"
    verbose_name = "Business Logic"
    label = "givesome"
    provides = {
        "xtheme": ["givesome.theme:GivesomeTheme"],
        "xtheme_resource_injection": [
            "shuup_firebase_auth.resources:add_resources",
            "givesome.resources:add_givesome_resources",
        ],
        "admin_module": [
            "givesome.admin_module.modules:GivesomeAdminProductModule",
            "givesome.admin_module.modules:GivesomeMultivendorProductsAdminModule",
            "givesome.admin_module.modules:SustainabilityGoalModule",
            "givesome.admin_module.modules:GivesomeOfficeProjectPromoteModule",
            "givesome.admin_module.modules:GivesomeVendorProjectPromoteModule",
            "givesome.admin_module.modules:GivesomeOfficeModule",
            "givesome.admin_module.modules:VendorInformationModule",
            "givesome.admin_module.modules:GivecardCampaignModule",
            "givesome.admin_module.modules:GivecardBatchModule",
            "givesome.admin_module.modules:GivesomePurseModule",
            "givesome.admin_module.modules:GivesomeMultivendorVendorAdminModule",
            "givesome.admin_module.modules:GivesomeVendorSettingsAdminModule",
            "givesome.admin_module.dashboard:GivesomeDashboardModule",
            "givesome.admin_module.modules:GivesomeReceiptingTextAdminModule",
            "givesome.admin_module.modules:GivesomeGifModule",
            "givesome.admin_module.modules:GivesomeCharityCompetitionModule",
            "givesome.admin_module.modules:GivesomeManageOrdersModule",
        ],
        "admin_givesome_gif_form_part": [
            "givesome.admin_module.form_parts.checkout_gif:GivesomeGifBaseFormPart",
        ],
        "admin_shop_form_part": [
            "givesome.admin_module.forms.shop_settings:GivesomeSettingsFormPart",
        ],
        "service_provider_admin_form": [
            "givesome.admin_module.forms.service_providers:GivecardPaymentProcessorForm",
        ],
        "front_urls": [
            "givesome.front.urls:urlpatterns",
        ],
        "admin_vendor_product_form_part": [
            "givesome.admin_module.form_parts.product:GivesomeVendorProductBaseFormPart",
            "givesome.admin_module.form_parts.product:GivesomeVendorShopProductFormPart",
            "givesome.admin_module.form_parts.product:GivesomeShopProductSustainabilityGoalFormPart",
            "givesome.admin_module.form_parts.product:GivesomeProjectExtraFormPart",
            "givesome.admin_module.completion_video:CompletionVideoURLFormPart",
        ],
        "givesome_charity_registration": ["givesome.front.providers:GivesomeRegistrationFormProvider"],
        "xtheme_plugin": [
            "givesome.plugins:GivesomeProductSelectionPlugin",
            "givesome.plugins:GivesomeProductSelectionWithOrderPlugin",
            "givesome.plugins:GivesomeVideoSelectionWithOrderPlugin",
            "givesome.plugins.homepage_vendors:HomepageVendorsPlugin",
            "givesome.plugins.vendor_information:VendorInformationPlugin",
        ],
        "admin_vendor_form_part": [
            "givesome.admin_module.form_parts.sustainability_goal_selection:VendorSustainabilityGoalFormPart",
            "givesome.admin_module.form_parts.vendor_extra:GivesomeVendorBaseFormPart",
            "givesome.admin_module.form_parts.supplier_office_term:SupplierOfficeTermFormPart",
        ],
        "front_extend_product_list_form": [
            "givesome.front.forms.sustainability_goals_filter:SustainabilityGoalsProjectListFilter",
            "givesome.front.product_list_modifiers:AvailableProductListFilter",
        ],
        "notify_event": [
            "givesome.signal_handlers:FullyFundedCharity",
        ],
        "admin_product_form_part": [
            "givesome.admin_module.views.progress_management:GivesomeSimpleSupplierFormPart",
            "givesome.admin_module.completion_video:CompletionVideoURLFormPart",
        ],
        "reports": [
            "givesome.admin_module.reports.campaign_reports:CampaignSummaryReport",
            "givesome.admin_module.reports.givecard_reports:GivecardDonationReport",
            "givesome.admin_module.reports.givecard_reports:GivecardRedemptionReport",
            "givesome.admin_module.reports.givesome_purse_reports:GivesomePurseChargeReport",
            "givesome.admin_module.reports.givesome_purse_reports:GivesomePurseManualDonateReport",
            "givesome.admin_module.reports.automatic_donation_reports:AllAutomaticDonationsReport",
            "givesome.admin_module.reports.receipting:ReceiptingReport",
        ],
    }

    def ready(self):
        import givesome.logging  # noqa
        import givesome.signal_handlers  # noqa
