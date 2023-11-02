# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _
from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import (
    CAMPAIGNS_MENU_CATEGORY,
    PRODUCTS_MENU_CATEGORY,
    SETTINGS_MENU_CATEGORY,
    ORDERS_MENU_CATEGORY,
)
from shuup.admin.modules.products import ProductModule
from shuup.admin.utils.urls import admin_url, derive_model_url, get_edit_and_list_urls
from shuup_multivendor.admin_module import (
    MultivendorProductsAdminModule,
    MultivendorVendorAdminModule,
    VendorSettingsAdminModule,
)

from givesome.models import (
    GivecardBatch,
    GivecardCampaign,
    GivesomeGif,
    GivesomeOffice,
    GivesomePurseAllocation,
    SustainabilityGoal,
    VendorInformation,
)


def override_urls(old_urls, new_urls):
    blacklist = [url.name for url in new_urls]
    urls = [url for url in old_urls if url.name not in blacklist]
    urls.extend(new_urls)
    return urls


class GivesomeMultivendorProductsAdminModule(MultivendorProductsAdminModule):
    def get_urls(self):
        urls = [
            admin_url(
                r"^multivendor/products/$",
                "givesome.admin_module.views.products.GivesomeProductListView",
                name="shuup_multivendor.products_list",
            ),
        ]
        return override_urls(super().get_urls(), urls)


class GivesomeAdminProductModule(ProductModule):
    def get_urls(self):
        urls = [
            admin_url(
                r"^products/(?P<pk>\d+)/$",
                "givesome.admin_module.views.products.GivesomeAdminProductEditView",
                name="shop_product.edit",
                permissions=("shop_product.edit",),
            ),
            admin_url(
                r"^products/new/$",
                "givesome.admin_module.views.products.GivesomeAdminProductEditView",
                name="shop_product.new",
                permissions=("shop_product.new",),
            ),
            admin_url(
                r"^products/$",
                "givesome.admin_module.views.products.GivesomeAdminProductListView",
                name="shop_product.list",
                permissions=("shop_product.list",),
            ),
        ]
        return override_urls(super().get_urls(), urls)


class GivesomeOfficeProjectPromoteModule(AdminModule):
    name = _("Office Project Promotion")
    breadcrumbs_menu_entry = MenuEntry(
        name, url="shuup_admin:office_project_promote.list"
    )

    def get_urls(self):
        urls = [
            admin_url(
                r"^multivendor/office_promote/$",
                "givesome.admin_module.views.project_promote.OfficeProjectPromoteListView",
                name="office_project_promote.list",
            ),
            admin_url(
                r"^multivendor/office_promote/(?P<pk>\d+)/$",
                "givesome.admin_module.views.project_promote.OfficeProjectPromoteEditView",
                name="office_project_promote.edit",
            ),
            admin_url(
                r"^multivendor/office_promote/toggle-promote/$",
                "givesome.admin_module.views.project_promote.OfficeTogglePromoteView",
                name="office_project_promote.toggle_promote",
            ),
            admin_url(
                r"^multivendor/office_promote/set-primary/$",
                "givesome.admin_module.views.project_promote.OfficeSetPrimaryView",
                name="office_project_promote.set_primary",
            ),
        ]
        return urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-handshake-o",
                url="shuup_admin:office_project_promote.list",
                category=PRODUCTS_MENU_CATEGORY,
            )
        ]


class GivesomeVendorProjectPromoteModule(AdminModule):
    name = _("Vendor Project Promotion")
    breadcrumbs_menu_entry = MenuEntry(
        name, url="shuup_admin:vendor_project_promote.list"
    )

    def get_urls(self):
        urls = [
            admin_url(
                r"^multivendor/vendor_promote/$",
                "givesome.admin_module.views.project_promote.VendorProjectPromoteListView",
                name="vendor_project_promote.list",
            ),
            admin_url(
                r"^multivendor/vendor_promote/(?P<pk>\d+)/$",
                "givesome.admin_module.views.project_promote.VendorProjectPromoteEditView",
                name="vendor_project_promote.edit",
            ),
            admin_url(
                r"^multivendor/vendor_promote/toggle-promote/$",
                "givesome.admin_module.views.project_promote.VendorTogglePromoteView",
                name="vendor_project_promote.toggle_promote",
            ),
            admin_url(
                r"^multivendor/vendor_promote/set-primary/$",
                "givesome.admin_module.views.project_promote.VendorSetPrimaryView",
                name="vendor_project_promote.set_primary",
            ),
            admin_url(
                r"^multivendor/vendor_promote/set-order/(?P<type>[a-z]+)/(?P<promoter_id>\d+)/"
                r"(?P<shop_product_id>\d+)/$",
                "givesome.admin_module.views.project_promote.OrderPromotedProjectsView",
                name="vendor_project_promote.set_order",
            ),
        ]
        return urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-handshake-o",
                url="shuup_admin:vendor_project_promote.list",
                category=PRODUCTS_MENU_CATEGORY,
            )
        ]


class GivesomeOfficeModule(AdminModule):
    name = _("Givesome Offices")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:office.list")

    def get_urls(self):
        return [
            admin_url(
                r"^office/delete/(?P<pk>\d+)/$",
                "givesome.admin_module.views.office.OfficeDeleteView",
                name="office.delete",
            )
        ] + get_edit_and_list_urls(
            url_prefix="^office",
            view_template="givesome.admin_module.views.office.Office%sView",
            name_template="office.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-building-o",
                url="shuup_admin:office.list",
                category=SETTINGS_MENU_CATEGORY,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(GivesomeOffice, "shuup_admin:office", object, kind)


class SustainabilityGoalModule(AdminModule):
    name = _("Sustainability Goal")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:sustainability_goal.list")

    def get_urls(self):
        urls = get_edit_and_list_urls(
            url_prefix="^sustainability_goal",
            view_template="givesome.admin_module.views.sustainability_goal.SustainabilityGoal%sView",
            name_template="sustainability_goal.%s",
        ) + [
            admin_url(
                r"^sustainability_goal/delete/(?P<pk>\d+)/$",
                "givesome.admin_module.views.sustainability_goal.SustainabilityGoalDeleteView",
                name="sustainability_goal.delete",
            )
        ]
        return urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-list",
                url="shuup_admin:sustainability_goal.list",
                category=SETTINGS_MENU_CATEGORY,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(
            SustainabilityGoal, "shuup_admin:sustainability_goal", object, kind
        )


class VendorInformationModule(AdminModule):
    name = "Vendor Information"
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:vendor_information.list")

    def get_urls(self):
        urls = get_edit_and_list_urls(
            url_prefix="^vendor_information",
            view_template="givesome.admin_module.views.vendor_information.VendorInformation%sView",
            name_template="vendor_information.%s",
        ) + [
            admin_url(
                r"^vendor_information/delete/(?P<pk>\d+)/$",
                "givesome.admin_module.views.vendor_information.VendorInformationDeleteView",
                name="vendor_information.delete",
            )
        ]
        return urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-list",
                url="shuup_admin:vendor_information.list",
                category=SETTINGS_MENU_CATEGORY,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(
            VendorInformation, "shuup_admin:vendor_information", object, kind
        )


class GivecardCampaignModule(AdminModule):
    name = _("Givecard Campaigns")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:givecard_campaign.list")

    def get_urls(self):
        return [
            admin_url(
                r"^givecard_campaign/delete/(?P<pk>\d+)/$",
                "givesome.admin_module.views.givecard_campaign.GivecardCampaignDeleteView",
                name="givecard_campaign.delete",
            )
        ] + get_edit_and_list_urls(
            url_prefix="^givecard_campaign",
            view_template="givesome.admin_module.views.givecard_campaign.GivecardCampaign%sView",
            name_template="givecard_campaign.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-bullhorn",
                url="shuup_admin:givecard_campaign.list",
                category=PRODUCTS_MENU_CATEGORY,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(
            GivecardCampaign, "shuup_admin:givecard_campaign", object, kind
        )


class GivecardBatchModule(AdminModule):
    name = _("Givecard Batches")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:givecard_batch.list")

    def get_urls(self):
        givecard_urls = [
            admin_url(
                r"^givecard_batch/delete/(?P<pk>\d+)/$",
                "givesome.admin_module.views.givecard_batch.GivecardBatchDeleteView",
                name="givecard_batch.delete",
            ),
            admin_url(
                r"^givecard_batch/(?P<pk>\d+)/givecards/$",
                "givesome.admin_module.views.givecard.GivecardListView",
                name="givecard.list",
            ),
            admin_url(
                r"^givecard_batch/generate/$",
                "givesome.admin_module.views.givecard.GivecardGenerateView",
                name="givecard.generate",
            ),
        ]

        batch_urls = [
            url
            for url in get_edit_and_list_urls(
                url_prefix="^givecard_batch",
                view_template="givesome.admin_module.views.givecard_batch.GivecardBatch%sView",
                name_template="givecard_batch.%s",
            )
            if url.name not in ["givecard_batch.list_settings"]
        ]

        multicard_urls = [
            admin_url(
                "multicard_batch/new/$",
                "givesome.admin_module.views.givecard_batch.MulticardBatchEditView",
                name="multicard_batch.new",
                kwargs={"pk": None},
                permissions=("givecard_batch.new",),
            ),
        ]

        return givecard_urls + batch_urls + multicard_urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-database",
                url="shuup_admin:givecard_batch.list",
                category=PRODUCTS_MENU_CATEGORY,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(
            GivecardBatch, "shuup_admin:givecard_batch", object, kind
        )


class GivesomePurseModule(AdminModule):
    name = _("Givesome Purse")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:givesome_purse.list")

    def get_urls(self):
        urls = [
            admin_url(
                r"^givesome_purse/$",
                "givesome.admin_module.views.givesome_purse.GivesomePurseListView",
                name="givesome_purse.list",
            ),
            admin_url(
                r"^givesome_purse/(?P<pk>\d+)/$",
                "givesome.admin_module.views.givesome_purse.GivesomePurseProjectListView",
                name="givesome_purse.project_list",
            ),
            admin_url(
                r"^givesome_purse/(?P<pk>\d+)/(?P<project_id>\d+)/$",
                "givesome.admin_module.views.givesome_purse.GivesomePurseAllocationEditView",
                name="givesome_purse.edit",
            ),
        ]
        return urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-balance-scale",
                url="shuup_admin:givesome_purse.list",
                category=PRODUCTS_MENU_CATEGORY,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(
            GivesomePurseAllocation, "shuup_admin:givesome_purse", object, kind
        )


class GivesomeMultivendorVendorAdminModule(MultivendorVendorAdminModule):
    def get_urls(self):
        urls = [
            admin_url(
                r"^vendor/$",
                "givesome.admin_module.views.vendor.GivesomeVendorListView",
                name="shuup_multivendor.vendor.list",
            ),
            admin_url(
                r"^vendor/(?P<pk>\d+)/$",
                "givesome.admin_module.views.vendor.GivesomeVendorEditView",
                name="shuup_multivendor.vendor.edit",
            ),
            admin_url(
                r"^vendor/new/$",
                "givesome.admin_module.views.vendor.GivesomeVendorEditView",
                name="shuup_multivendor.vendor.new",
            ),
        ]
        return override_urls(old_urls=super().get_urls(), new_urls=urls)


class GivesomeVendorSettingsAdminModule(VendorSettingsAdminModule):
    def get_urls(self):
        return [
            admin_url(
                r"^multivendor/settings/$",
                "givesome.admin_module.views.vendor.GivesomeVendorSettingsView",
                name="shuup_multivendor.vendor.settings",
            )
        ]


class GivesomeGifModule(AdminModule):
    name = _("Givesome checkout gif")
    category = _("Givesome checkout gif")
    breadcrumbs_menu_entry = MenuEntry(
        text=name, url="shuup_admin:givesome_gif.list", category=PRODUCTS_MENU_CATEGORY
    )

    def get_urls(self):
        return [
            admin_url(
                r"^checkout_gif/(?P<pk>\d+)/delete/$",
                "givesome.admin_module.views.checkout_gif.GivesomeGifDeleteView",
                name="givesome_gif.delete",
            ),
        ] + get_edit_and_list_urls(
            url_prefix="^checkout_gif",
            view_template="givesome.admin_module.views.checkout_gif.GivesomeGif%sView",
            name_template="givesome_gif.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Checkout gif"),
                icon="fa fa-sitemap",
                url="shuup_admin:givesome_gif.list",
                category=PRODUCTS_MENU_CATEGORY,
                ordering=2,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(GivesomeGif, "shuup_admin:givesome_gif", object, kind)


class GivesomeReceiptingTextAdminModule(AdminModule):
    name = _("Receipting Messages")

    def get_urls(self):
        return [
            admin_url(
                r"^receipting_messages/$",
                "givesome.admin_module.views.receipting_messages.ReceiptingMessagesEditView",
                name="receipting_messages.edit",
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-university",
                url="shuup_admin:receipting_messages.edit",
                category=SETTINGS_MENU_CATEGORY,
            )
        ]


class GivesomeCharityCompetitionModule(AdminModule):
    name = _("Manage Competitions")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:charity_competition.list")

    def get_urls(self):
        urls = [
            admin_url(
                r"^charity_competitions/$",
                "givesome.admin_module.views.charity_competition.CharityCompetitionListView",
                name="charity_competition.list",
            ),
            admin_url(
                r"^charity_competitions/(?P<pk>\d+)/$",
                "givesome.admin_module.views.charity_competition.CharityCompetitionEditView",
                name="charity_competition.edit",
            ),
            admin_url(
                r"^charity_competitions/new/$",
                "givesome.admin_module.views.charity_competition.CharityCompetitionEditView",
                name="charity_competition.new",
            ),
        ]
        return urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-handshake-o",
                url="shuup_admin:charity_competition.list",
                category=PRODUCTS_MENU_CATEGORY,
            ),
            MenuEntry(
                text="New Competition",
                icon="fa fa-handshake-o",
                url="shuup_admin:charity_competition.new",
                category=PRODUCTS_MENU_CATEGORY,
            ),
        ]


class GivesomeManageOrdersModule(AdminModule):
    name = _("Delete Orders")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:manage_orders.list")

    def get_urls(self):
        urls = [
            admin_url(
                r"^manage_orders/$",
                "givesome.admin_module.views.manage_orders.ManageOrdersListView",
                name="manage_orders.list",
            ),
            admin_url(
                r"^manage_orders/(?P<pk>\d+)/$",
                "givesome.admin_module.views.manage_orders.ManageOrdersEditView",
                name="manage_orders.edit",
            ),
            admin_url(
                r"^manage_orders/delete/(?P<pk>\d+)/$",
                "givesome.admin_module.views.manage_orders.delete_order",
                name="manage_orders.delete",
            ),
        ]
        return urls

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-handshake-o",
                url="shuup_admin:manage_orders.list",
                category=ORDERS_MENU_CATEGORY,
            ),
        ]
