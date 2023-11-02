# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

import six
from django import forms
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django_countries import countries
from django_countries.fields import LazyTypedChoiceField
from enumfields import Enum, EnumField

from shuup import configuration
from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.forms.fields import ListToCommaSeparatedStringField
from shuup.admin.modules.settings.enums import OrderReferenceNumberMethod
from shuup.admin.utils.permissions import has_permission
from shuup.apps.provides import get_provide_objects
from shuup.core.models import ConfigurationItem, Currency, EncryptedConfigurationItem
from shuup.core.pricing import get_discount_modules
from shuup.core.setting_keys import SHUUP_DISCOUNT_MODULES, SHUUP_HOME_CURRENCY, SHUUP_PRICING_MODULE
from shuup.core.tasks import run_task


class BaseSettingsFormPart(FormPart):
    name = "base_settings"
    form = None  # override in subclass

    def has_permission(self):
        return True

    def get_form_defs(self):
        if not self.has_permission():
            return

        yield TemplatedFormDef(
            self.name,
            self.form,
            required=False,
            template_name="shuup/admin/settings/form_parts/settings_base.jinja",
            kwargs={"request": self.request},
        )

    def _delete_configuration_items(self, form):
        for key in form.fields.keys():
            try:
                key_deleted = ConfigurationItem.objects.get(shop=None, key=key).delete()
            except ConfigurationItem.DoesNotExist:
                key_deleted = False
            if not key_deleted:
                try:
                    EncryptedConfigurationItem.objects.get(shop=None, key=key).delete()
                except EncryptedConfigurationItem.DoesNotExist:
                    pass

    def save(self, form):
        if not form.has_changed():
            return False  # no need to save

        self._delete_configuration_items(form)
        for key, value in six.iteritems(form.cleaned_data):
            if isinstance(value, Enum):
                value = value.value
            if isinstance(value, models.Model):
                value = str(value)
            encrypt = key in form.encrypted_fields
            configuration.set(None, key, value, encrypted=encrypt)
        return True


class BaseSettingsForm(forms.Form):
    title = None
    encrypted_fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(BaseSettingsForm, self).__init__(*args, **kwargs)

        for field in self.fields.keys():
            self.fields[field].initial = configuration.get(None, field)

        if self.data:
            # The html input of type checkout doesn't send the value if False. Here we force it to uncheck the value.
            for field in self.fields:
                if isinstance(self.fields[field], forms.BooleanField):
                    if "%s-%s" % (self.prefix, field) not in self.data:
                        self.fields[field].value = False


class InstallationSettingsForm(BaseSettingsForm):
    title = _("Installation Settings")

    pricing_module = forms.ChoiceField(
        label=_("Pricing Module"),
        choices=[(module.identifier, module.name) for module in get_provide_objects("pricing_module")],
        help_text=_(
            "The pricing module that should be used for pricing products. It determines how product prices are "
            "calculated. Warning: all prices will be reindexed once the pricing module is changed."
        ),
        required=True,
    )
    discount_modules = forms.MultipleChoiceField(
        label=_("Discount Modules"),
        initial=lambda: configuration.get(None, SHUUP_DISCOUNT_MODULES),
        choices=lambda: [(module.identifier, module.name) for module in get_discount_modules()],
        help_text=_(
            "The list of discount modules to use in the platform. "
            "Each discount module may change the price of a product."
        ),
        required=False,
    )
    tax_module = forms.ChoiceField(
        label=_("Tax Module"),
        choices=[(module.identifier, module.name) for module in get_provide_objects("tax_module")],
        help_text=_(
            "The tax module used to determining taxes of products and order lines. "
            "Determines taxation rules for products, shipping/payment methods and other order items."
        ),
        required=True,
    )
    order_source_modifier_modules = forms.MultipleChoiceField(
        label=_("Order Source Modifier Modules"),
        choices=[(module.identifier, module.name) for module in get_provide_objects("order_source_modifier_module")],
        help_text=_("The list of modules of order source modifiers."),
        required=False,
    )
    enable_multiple_shops = forms.BooleanField(
        label=_("Enable Multiple Shops"),
        help_text=_(
            "Whether multiple shops are expected to be enabled in this installation. "
            "Enabling or disabling this flag does not make it (im)possible to set up multiple shops, "
            "but having it disabled may give a small performance increase."
        ),
        required=False,
    )
    enable_multiple_suppliers = forms.BooleanField(
        label=_("Enable Multiple Suppliers"),
        help_text=_(
            "Whether multiple suppliers are enabled in this installation. "
            "Enabling this flag allows supplier creation from Admin Panel."
        ),
        required=False,
    )
    manage_contacts_per_shop = forms.BooleanField(
        label=_("Manage Contacts Per Shop"),
        help_text=_(
            "Indicates whether Shuup should restrict Contact access per Shop. "
            "This is useful when multi-shop is in use and the contact shouldn't "
            "be visible by other shops. "
            "When enabled, the contact will only be visible for shops in which user."
        ),
        required=False,
    )
    enable_attributes = forms.BooleanField(
        label=_("Enable Attributes"),
        help_text=_(
            "Whether product attributes are enabled. For installations not requiring attributes, "
            "disabling this may give a small performance increase."
        ),
        required=False,
    )
    telemetry_enabled = forms.BooleanField(
        label=_("Enable Telemetry"),
        help_text=_("The flag to enable/disable the telemetry (statistics) system."),
        required=False,
    )


class InstallationSettingsFormPart(BaseSettingsFormPart):
    form = InstallationSettingsForm
    name = "installation_settings"
    priority = 0

    def has_permission(self):
        # only super users can configure the installation
        return self.request.user.is_superuser

    def save(self, form):
        needs_reindexing = False
        if not (form.cleaned_data["discount_modules"] == configuration.get(None, SHUUP_DISCOUNT_MODULES)) or not (
            form.cleaned_data["pricing_module"] == configuration.get(None, SHUUP_PRICING_MODULE)
        ):
            needs_reindexing = True
        super().save(form)
        if needs_reindexing:
            transaction.on_commit(lambda: run_task("shuup.core.catalog.utils.reindex_all_shop_products"))


class OrderSettingsForm(BaseSettingsForm):
    title = _("Order Settings")
    order_reference_number_method = EnumField(OrderReferenceNumberMethod).formfield(
        label=_("Order Reference number method"),
        help_text=_(
            "This option defines how the reference numbers for orders are built. The options are:"
            "<br><br><b>Unique</b><br>Order reference number is unique system wide, "
            "regardless of the amount of shops."
            "<br><br><b>Running</b><br>Order number is running system wide, regardless of the amount of shops."
            "<br><br><b>Shop Running</b><br>Every shop has its own running numbers for reference."
        ),
        required=True,
    )
    order_reference_number_length = forms.IntegerField(
        label=_("Order Reference number length"),
        help_text=_("The default length of reference numbers generated by certain reference number generators."),
        required=True,
    )
    order_reference_number_prefix = forms.CharField(
        label=_("Order Reference number prefix"),
        help_text=_("An arbitrary (numeric) default prefix for certain reference number generators."),
        required=False,
    )
    allow_editing_order = forms.BooleanField(
        label=_("Allow Editing Order"),
        help_text=_(
            "Whether to allow editing order. "
            "By default when multiple suppliers is enabled this option is disabled "
            "since order edit does not offer supplier select for product line. "
            "You can enable this when there is max one vendor per product."
        ),
        required=False,
    )
    allow_anonymous_orders = forms.BooleanField(
        label=_("Allow Anonymous Orders"),
        help_text=_("Whether or not anonymous orders (without a `creator` user) are allowed."),
        required=False,
    )
    allow_arbitrary_refunds = forms.BooleanField(
        label=_("Allow Arbitrary Refunds"),
        help_text=_(
            "Whether to allow to create arbitrary refunds. Set this to False when it is "
            "required that all refunds are linked to the actual order items/lines."
        ),
        required=False,
    )
    default_order_label = forms.CharField(
        label=_("Default Order Label"),
        help_text=_("The order label to apply to orders by default."),
        required=False,
    )


class OrderSettingsFormPart(BaseSettingsFormPart):
    form = OrderSettingsForm
    name = "order_settings"
    priority = 3

    def has_permission(self):
        return has_permission(self.request.user, "system_settings.order_settings")


class CoreSettingsForm(BaseSettingsForm):
    title = _("Core Settings")
    home_currency = forms.ModelChoiceField(
        label=_("Home Currency"),
        queryset=Currency.objects.all(),
        help_text=_(
            "This option defines the currency in that all the monetary values are expressed. "
            "Enter a valid ISO-4217 currency code."
        ),
        required=True,
    )
    address_home_country = LazyTypedChoiceField(
        label=_("Home Country"),
        choices=[("", _("Select Country"))] + list(countries),
        help_text=_(
            "This option defines the home country of the system. It will configure the default country for "
            "order addresses. The home country must be a code (ISO 3166-1 alpha 2) for the Shuup installation. "
            "If empty, among other things, addresses that would be printed with the country visible, are printed "
            "with no country."
        ),
        required=True,
    )
    calculate_taxes_automatically_if_possible = forms.BooleanField(
        label=_("Calculate Taxes Automatically If Possible"),
        help_text=_(
            "Whether taxes should be calculated automatically. Perhaps you "
            "don't need it if you are selling to a specific group of customers (foreigners, businesses), "
            "where automatic tax calculation is not needed."
        ),
        required=False,
    )
    allowed_upload_extensions = ListToCommaSeparatedStringField(
        label=_("Allowed Upload File Extensions"),
        initial=["pdf", "png", "jpeg", "jpg"],
        help_text=_("List of allowed extensions for file or image uploads."),
        required=True,
    )
    max_upload_size = forms.IntegerField(
        label=_("Max Upload Size"),
        initial=500000,
        help_text=_("Maximum allowed file size (in bytes) for uploads."),
        required=False,
    )
    mass_unit = forms.ChoiceField(
        label=_("Mass Unit"),
        choices=(
            ("kg", _("Kilogram")),
            ("g", _("Gram")),
            ("lb", _("Pound")),
        ),
        help_text=_("The mass/weight unit that Shuup should use."),
        required=True,
    )
    length_unit = forms.ChoiceField(
        label=_("Length Unit"),
        choices=(
            ("mm", _("Millimeter")),
            ("cm", _("Centimeter")),
            ("m", _("Meter")),
            ("km", _("Kilometer")),
            ("in", _("Inch")),
            ("ft", _("Foot")),
            ("yd", _("Yard")),
            ("mi", _("Mile")),
        ),
        help_text=_(
            "The length/distance unit that Shuup should use. "
            "All area values will use this unit raised to the power of 2."
        ),
        required=True,
    )
    volume_unit = forms.ChoiceField(
        label=_("Volume Unit"),
        choices=(
            ("mm3", _("Cubic Millimeter")),
            ("cm3", _("Cubic Centimeter")),
            ("m3", _("Cubic Meter")),
            ("km3", _("Cubic Kilometer")),
            ("in3", _("Cubic Inch")),
            ("ft3", _("Cubic Foot")),
            ("yd3", _("Cubic Yard")),
            ("mi3", _("Cubic Mile")),
        ),
        help_text=_("The volume unit that Shuup should use."),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(CoreSettingsForm, self).__init__(*args, **kwargs)
        self.fields[SHUUP_HOME_CURRENCY].initial = Currency.objects.filter(
            code=configuration.get(None, SHUUP_HOME_CURRENCY)
        ).first()


class CoreSettingsFormPart(BaseSettingsFormPart):
    form = CoreSettingsForm
    name = "core_settings"
    priority = 1

    def has_permission(self):
        return has_permission(self.request.user, "system_settings.core_settings")


class AdminSettingsForm(BaseSettingsForm):
    title = _("Admin Settings")
    admin_allow_html_in_product_description = forms.BooleanField(
        label=_("Allow Html In Product Description"),
        help_text=_(
            "Whether to allow vendors and staff the use of rich text editor and HTML for their product descriptions. "
            "If this is False, only allow simple text field and sanitize all HTML from it."
        ),
        required=False,
    )
    admin_allow_html_in_supplier_description = forms.BooleanField(
        label=_("Allow Html In Supplier Description"),
        help_text=_(
            "Whether to allow the use of rich text editor and HTML for their profile descriptions. "
            "If this is False, only a allow simple text field and sanitize all HTML from it."
        ),
        required=False,
    )


class AdminSettingsFormPart(BaseSettingsFormPart):
    form = AdminSettingsForm
    name = "admin_settings"
    priority = 2

    def has_permission(self):
        return has_permission(self.request.user, "system_settings.admin_settings")
