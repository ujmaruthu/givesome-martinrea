# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import os

import dj_database_url
import environ
import sentry_sdk
from django import forms
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env(DEBUG=(bool, False))


def optenv(var):
    return env(var, default=None)


root = environ.Path(__file__) - 3

BASE_DIR = root()

DEBUG = env("DEBUG")

env.read_env(os.path.join(BASE_DIR, "app", ".env"))

SECRET_KEY = env("SECRET_KEY")

DATABASES = {"default": dj_database_url.config()}

# accept emojis in MYSQL
if DATABASES["default"]["ENGINE"].startswith("django.db.backends.mysql"):
    DATABASES["default"].update({"OPTIONS": {"charset": "utf8mb4"}})

MEDIA_URL = env("MEDIA_URL", default="/media/")
STATIC_URL = env("STATIC_URL", default="/static/")

MEDIA_ROOT = root(env("MEDIA_LOCATION", default=os.path.join(BASE_DIR, "var", "media")))
STATIC_ROOT = root(env("STATIC_LOCATION", default=os.path.join(BASE_DIR, "var", "static")))

SHUUP_HOME_CURRENCY = "CAD"

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="*").split(",")


if env("EMAIL_URL", default=None):
    EMAIL_CONFIG = env.email_url("EMAIL_URL")
    vars().update(EMAIL_CONFIG)
else:
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, "var", "emails")
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"


BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.redirects",
    "django.contrib.sitemaps",
    # external apps that need to be loaded before Shuup
    "easy_thumbnails",
]

INSTALLED_APPS = BASE_APPS + [
    # Shuup
    "givesome_admin",
    "givesome",
    "shuup.themes.classic_gray",
    "shuup_definite_theme",
    "shuup_multivendor",  # Overrides base for fun
    "shuup.admin",
    "shuup.core",
    "shuup.default_tax",
    "shuup.front",
    "shuup.front.apps.auth",
    "shuup.front.apps.carousel",
    "shuup.front.apps.customer_information",
    "shuup.front.apps.personal_order_history",
    "shuup.front.apps.registration",
    "shuup.front.apps.simple_order_notification",
    "shuup.front.apps.simple_search",
    "shuup.notify",
    "shuup.simple_cms",
    "shuup.discounts",
    "shuup.campaigns",
    "shuup.customer_group_pricing",
    "shuup.simple_supplier",
    "shuup.order_printouts",
    "shuup.utils",
    "shuup.xtheme",
    "shuup.reports",
    "shuup.default_reports",
    "shuup.regions",
    "shuup.importer",
    "shuup.default_importer",
    "shuup_api",
    "shuup_rest_api",
    "shuup_can_taxes",
    "shuup_category_organizer",
    "shuup_xtheme_extra_layouts",
    "shuup_subscriptions",
    "shuup_stripe_subscriptions",
    "shuup_wishlist",
    "shuup_stripe_multivendor",
    "shuup_cms_blog",
    "shuup_mailchimp",
    "shuup_typography",
    "shuup.gdpr",
    "shuup.tasks",
    "shuup_logging",
    "shuup_messages",
    "shuup_favorite_vendors",
    "shuup_sent_emails",
    "shuup_sitemap",
    "shuup_firebase_auth",
    "shuup_project_tracking",
    "shuup_multicurrencies_display",
    # Externals
    "bootstrap3",
    "django_countries",
    "django_jinja",
    "django_crontab",
    "filer",
    "registration",
    "reversion",
    "rest_framework",
    "rest_framework_swagger",
]

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "shuup.front.middleware.ProblemMiddleware",
    "shuup.front.middleware.ShuupFrontMiddleware",
    "shuup.xtheme.middleware.XthemeMiddleware",
    "shuup.admin.middleware.ShuupAdminMiddleware",
    "shuup_multivendor.middleware.ShuupMultivendorAdminMiddleware",
    "givesome.middleware.ActivateTimezoneMiddleware",
)

# if DEBUG:
#     def show_toolbar(request):
#         return True
#
#     INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar"]
#     MIDDLEWARE = MIDDLEWARE + ("debug_toolbar.middleware.DebugToolbarMiddleware",)
#
#     DEBUG_TOOLBAR_CONFIG = {
#         "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
#     }
#     del DATABASES['default']['OPTIONS']['sslmode']
#     del INSTALLED_APPS[5]


ROOT_URLCONF = "project.urls"
WSGI_APPLICATION = "project.wsgi.application"
LANGUAGE_CODE = "en"
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login/"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@myshuup.com")

SITE_ID = env("SITE_ID", default=1)

LANGUAGE_CHOICES = [
    ("en", "English"),
    ("fr-ca", "French"),
]

selected_languages = "en,fr-ca".split(",")
LANGUAGES = [(code, name) for code, name in LANGUAGE_CHOICES if code in selected_languages]

PARLER_DEFAULT_LANGUAGE_CODE = default = "en"

PARLER_LANGUAGES = {None: [{"code": c, "name": n} for (c, n) in LANGUAGES], "default": {"hide_untranslated": False}}

_TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.request",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
]

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".jinja",
            "context_processors": _TEMPLATE_CONTEXT_PROCESSORS,
            "newstyle_gettext": True,
            "environment": "shuup.xtheme.engine.XthemeEnvironment",
        },
        "NAME": "jinja2",
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": _TEMPLATE_CONTEXT_PROCESSORS, "debug": DEBUG},
    },
]

CACHES = {"default": env.cache(default="memcache://127.0.0.1:11211")}


# Shuup Firebase Auth
FIREBASE_AUTH_API_KEY = env("FIREBASE_AUTH_API_KEY", default=None)
FIREBASE_AUTH_AUTH_DOMAIN = env("FIREBASE_AUTH_AUTH_DOMAIN", default=None)
FIREBASE_AUTH_DATABASE_URL = env("FIREBASE_AUTH_DATABASE_URL", default=None)
FIREBASE_AUTH_PROJECT_ID = env("FIREBASE_AUTH_PROJECT_ID", default=None)
FIREBASE_AUTH_STORAGE_BUCKET = env("FIREBASE_AUTH_STORAGE_BUCKET", default=None)
FIREBASE_AUTH_MESSAGING_SENDER_ID = env("FIREBASE_AUTH_MESSAGING_SENDER_ID", default=None)
FIREBASE_AUTH_APP_ID = env("FIREBASE_AUTH_APP_ID", default=None)

SHUUP_FIREBASE_AUTH_PROVIDERS = [
    "email",
    "google",
    "facebook"
]
SHUUP_FIREBASE_AUTH_PROVIDER_ARGS = {
    "email": {
        "fullLabel": "Sign up with email",
    },
    "google": {
        "fullLabel": "Sign up with Google",
    },
    "facebook": {
        "fullLabel": "Sign up with Facebook",
    },
    # "apple": {
    #     "fullLabel": "Sign up with Apple",
    # },
}
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_TYPE = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_TYPE", default=None)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PROJECT_ID = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PROJECT_ID", default=None)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PRIVATE_KEY_ID = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PRIVATE_KEY_ID", default=None)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PRIVATE_KEY = env.str(
    "SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PRIVATE_KEY", multiline=True, default=""
)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_EMAIL = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_EMAIL", default=None)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_ID = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_ID", default=None)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_AUTH_URI = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_AUTH_URI", default=None)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_TOKEN_URI = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_TOKEN_URI", default=None)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_AUTH_PROVIDER_CERT_URL = env(
    "SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_AUTH_PROVIDER_CERT_URL", default=None
)
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_CERT_URL = env("SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_CERT_URL", default=None)
if (
    FIREBASE_AUTH_API_KEY
    and FIREBASE_AUTH_AUTH_DOMAIN
    and FIREBASE_AUTH_PROJECT_ID
    and FIREBASE_AUTH_STORAGE_BUCKET
    and FIREBASE_AUTH_MESSAGING_SENDER_ID
    and FIREBASE_AUTH_APP_ID
):
    SHUUP_FIREBASE_AUTH_SETTINGS = {
        "API_KEY": FIREBASE_AUTH_API_KEY,
        "AUTH_DOMAIN": FIREBASE_AUTH_AUTH_DOMAIN,
        "PROJECT_ID": FIREBASE_AUTH_PROJECT_ID,
        "STORAGE_BUCKET": FIREBASE_AUTH_STORAGE_BUCKET,
        "MESSAGING_SENDER_ID": FIREBASE_AUTH_MESSAGING_SENDER_ID,
        "APP_ID": FIREBASE_AUTH_MESSAGING_SENDER_ID,
    }

    SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_DICT = {
        "type": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_TYPE,
        "project_id": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PROJECT_ID,
        "private_key_id": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PRIVATE_KEY_ID,
        "private_key": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_PRIVATE_KEY,
        "client_email": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_EMAIL,
        "client_id": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_ID,
        "auth_uri": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_AUTH_URI,
        "token_uri": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_TOKEN_URI,
        "auth_provider_x509_cert_url": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_AUTH_PROVIDER_CERT_URL,
        "client_x509_cert_url": SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_CLIENT_CERT_URL,
    }

SHUUP_SETUP_WIZARD_PANE_SPEC = []

SHUUP_ERROR_PAGE_HANDLERS_SPEC = [
    "shuup.admin.error_handlers:AdminPageErrorHandler",
    "shuup.front.error_handlers:FrontPageErrorHandler",
]

SHUUP_SIMPLE_SEARCH_LIMIT = 50

# Permissions
STAFF_PERMISSION_GROUP_NAME = "Staff"
VENDORS_PERMISSION_GROUP_NAME = "Vendors"

# Shuup (shuup.core)
SHUUP_ENABLE_MULTIPLE_SHOPS = False  # For multivendor marketplace multiple shops is not supported
SHUUP_ENABLE_MULTIPLE_SUPPLIERS = True
SHUUP_MANAGE_CONTACTS_PER_SHOP = True

SHUUP_PRICING_MODULE = "multivendor_supplier_pricing"
SHUUP_SHOP_PRODUCT_SUPPLIERS_STRATEGY = "shuup_multivendor.supplier_strategy:CheapestSupplierPriceSupplierStrategy"

SHUUP_REQUEST_SHOP_PROVIDER_SPEC = "givesome.core_shop_provider.DefaultShopProvider"

USA_TAX_DEFAULT_TAX_IDENTIFIER = CAN_TAX_DEFAULT_TAX_IDENTIFIER = "Default tax class"
USA_TAX_ADDITIONAL_TAX_CLASS_IDENTIFIERS = []

SHUUP_PROVIDES_BLACKLIST = {
    "admin_module": [
        "shuup.admin.modules.products:ProductModule",
        "shuup.admin.modules.support:ShuupSupportModule",
        "shuup.testing.modules.sample_data:SampleDataAdminModule",
        "shuup.testing.modules.demo:DemoModule",
        "shuup.testing.modules.mocker:TestingAdminModule",
        "shuup_multivendor.admin_module:MultivendorProductsAdminModule",
        "shuup_multivendor.admin_module:MultivendorVendorAdminModule",
        "shuup_multivendor.admin_module:VendorSettingsAdminModule",
        "shuup_multivendor.dashboards:SalesDashboardModule",
    ],
    "admin_order_section": [
        "shuup.admin.modules.orders.sections:BasicDetailsOrderSection",
    ],
    "service_provider_admin_form": [
        "shuup.testing.service_forms:PseudoPaymentProcessorForm",
        "shuup.testing.service_forms:PaymentWithCheckoutPhaseForm",
        "shuup.testing.service_forms:CarrierWithCheckoutPhaseForm",
    ],
    "front_service_checkout_phase_provider": [
        "shuup.testing.simple_checkout_phase.PaymentPhaseProvider",
        "shuup.testing.simple_checkout_phase.ShipmentPhaseProvider",
    ],
    "admin_contact_toolbar_button": [
        "shuup.testing.modules.mocker.toolbar:MockContactToolbarButton",
    ],
    "admin_contact_toolbar_action_item": [
        "shuup.testing.modules.mocker.toolbar:MockContactToolbarActionItem",
    ],
    "admin_contact_edit_toolbar_button": [
        "shuup.testing.modules.mocker.toolbar:MockContactToolbarButton",
    ],
    "admin_shop_edit_toolbar_button": [
        "shuup.testing.modules.mocker.toolbar:MockShopToolbarButton",
    ],
    "admin_product_toolbar_action_item": [
        "shuup.testing.modules.mocker.toolbar:MockProductToolbarActionItem",
    ],
    "admin_contact_section": [
        "shuup.testing.modules.mocker.sections:MockContactSection",
    ],
    "importers": ["shuup.testing.importers.DummyImporter", "shuup.testing.importers.DummyFileImporter"],
    "xtheme": [
        "shuup.testing.themes:ShuupTestingTheme",
        "shuup.testing.themes:ShuupTestingThemeWithCustomBase",
    ],
    "xtheme_plugin": [
        "shuup.xtheme.plugins.products:ProductHighlightPlugin",
    ],
    "pricing_module": ["shuup.testing.supplier_pricing.pricing:SupplierPricingModule"],
    "admin_vendor_form_part": [
        # shuup-opening-hours provides a drop-in replacement for this.
        "shuup_multivendor.admin_module.form_parts.vendor:VendorOpeningPeriodsFormPart",
        "shuup_stripe_multivendor.admin_module.form_parts.vendor_commission:"
        "StripeSupplierCustomCommissionsRatesFormPart",
        "shuup_multivendor.admin_module.form_parts.vendor:VendorBaseFormPart",
    ],
    "customer_dashboard_items": [
        # Doesn't work with shuup-stripe-multivendor.
        "shuup_stripe.dashboard_items:SavedPaymentInfoDashboardItem",
        "shuup_wishlist.dashboard_items:WishlistItem",
        "shuup_cms_blog.dashboard_items:SavedArticlesDashboardItem",
        "shuup_messages.dashboard_items:MessagesDashboardItem",
        "shuup.gdpr.dashboard_items:GDPRDashboardItem",
        "shuup.front.apps.customer_information.dashboard_items:CompanyDashboardItem",
        "shuup.front.apps.customer_information.dashboard_items:AddressBookDashboardItem",
        "shuup.front.apps.personal_order_history.dashboard_items:OrderHistoryItem",
        "shuup_multicurrencies_display.customer_information.dashboard_items:PreferredCurrencyItem",
    ],
    "notify_event": ["shuup.simple_supplier.notify_events:AlertLimitReached"],
    "notify_script_template": [
        "shuup.simple_supplier.notify_script_template:StockLimitEmailScriptTemplate",
    ],
    "admin_product_form_part": [
        "shuup.customer_group_pricing.admin_form_part:CustomerGroupPricingFormPart",
        "shuup.customer_group_pricing.admin_form_part:CustomerGroupPricingDiscountFormPart",
        "shuup.simple_supplier.admin_module.forms:SimpleSupplierFormPart",
        "shuup.admin.modules.products.views.edit.ProductBaseFormPart",
        "shuup.admin.modules.products.views.edit.ShopProductFormPart",
    ],
    "admin_vendor_product_form_part": [
        "shuup_multivendor.admin_module.form_parts.product:VendorProductBaseFormPart",
        "shuup_multivendor.admin_module.form_parts.product:VendorShopProductFormPart",
        "shuup_multivendor.admin_module.form_parts.simple_supplier:SimpleSupplierFormPart",
        "shuup_multivendor.admin_module.form_parts.location:ProductSupplierLocationFormPart",
    ],
    "reports": [
        "shuup.default_reports.reports.shipping:ShippingReport",
        "shuup.default_reports.reports.refunds.RefundedSalesReport",
        "shuup.default_reports.reports.taxes:TaxesReport",
        "shuup.default_reports.reports.orders.OrdersReport",
        "shuup.default_reports.reports.orders.OrderLineReport",
        "shuup_multivendor.reports:ProductReport",
    ],
    "front_urls_post": ["shuup.simple_cms.urls:urlpatterns"],
}

# Shuup (shuup.admin)
SHUUP_ADMIN_SHOP_PROVIDER_SPEC = "givesome.admin_shop_provider.AdminShopProvider"
SHUUP_ADMIN_SUPPLIER_PROVIDER_SPEC = "givesome.supplier_provider.MultivendorSupplierProvider"
SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION = True
SHUUP_ADMIN_ALLOW_HTML_IN_VENDOR_DESCRIPTION = True
SHUUP_ADMIN_MINIMUM_INPUT_LENGTH_SEARCH = 1

# Shuup (shuup.front)
# Basket and order creator settings
SHUUP_CHECKOUT_VIEW_SPEC = env(
    "SHUUP_CHECKOUT_VIEW_SPEC", default="givesome.front.views:CheckoutViewWithLoginAndRegisterVertical"
)
SHUUP_BASKET_CLASS_SPEC = env("SHUUP_BASKET_CLASS_SPEC", default="shuup.front.basket.objects:BaseBasket")
SHUUP_BASKET_ORDER_CREATOR_SPEC = env(
    "SHUUP_BASKET_ORDER_CREATOR_SPEC", default="shuup.core.basket.order_creator:BasketOrderCreator"
)
SHUUP_FRONT_OVERRIDE_SORTS_AND_FILTERS_LABELS_LOGIC = {"manufacturers": "Brands", "supplier": "Filter by vendor"}
SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD = False
SHUUP_PERSON_CONTACT_FIELD_PROPERTIES = {
    "phone": {"widget": forms.HiddenInput()},
    "timezone": {"widget": forms.HiddenInput()},
    "marketing_permission": {"widget": forms.HiddenInput()},
}

SHUUP_ORDER_SOURCE_MODIFIER_MODULES = []
REWARD_POINTS_SPENT_ACCOUNTING_IDENTIFIER = ""
SHUUP_ALLOW_ANONYMOUS_ORDERS = True

# Shuup Stripe Connect
STRIPE_WEBHOOK_SLUG = env("STRIPE_WEBHOOK_SLUG", default="callback")
STRIPE_WEBHOOK_KEY = env("STRIPE_WEBHOOK_KEY", default=None)
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default=None)
STRIPE_PUBLIC_KEY = env("STRIPE_PUBLIC_KEY", default=None)
STRIPE_OAUTH_CLIENT_ID = env("STRIPE_OAUTH_CLIENT_ID", default=None)
STRIPE_SUBSCRIPTIONS_API_VERSION = env("STRIPE_SUBSCRIPTIONS_API_VERSION", default="2018")

# Shuup (shuup.front.apps.registration)
SHUUP_REGISTRATION_REQUIRES_ACTIVATION = env.bool("SHUUP_REGISTRATION_REQUIRES_ACTIVATION", default=False)

# Shuup Multivendor
SHUUP_ADDRESS_HOME_COUNTRY = env("SHUUP_ADDRESS_HOME_COUNTRY", default="CA")
VENDOR_CAN_SHARE_PRODUCTS = False
SHUUP_MULTIVENDOR_ENABLE_CUSTOM_PRODUCTS = True
SHUUP_MULTIVENDOR_SUPPLIER_MODULE_IDENTIFIER = "simple_supplier"
SHUUP_MULTIVENDOR_SUPPLIER_STOCK_MANAGED_BY_DEFAULT = True
SHUUP_MULTIVENDOR_PRODUCTS_REQUIRES_APPROVAL_DEFAULT = True
SHUUP_MULTIVENDOR_VENDOR_REQUIRES_APPROVAL = True

SHUUP_MULTIVENDOR_REGISTRATION_COUNTRIES = ["CA", "US"]
SHUUP_MULTIVENDOR_GOOGLE_MAPS_KEY = env("SHUUP_MULTIVENDOR_GOOGLE_MAPS_KEY", default=None)
SHUUP_MULTIVENDOR_ENSURE_ADDRESS_GEOPOSITION = False  # Not needed in this marketplace
SHUUP_MULTIVENDOR_CALCULATE_VENDOR_DISTANCE = False  # Not needed in this marketplace
SHUUP_MULTIVENDOR_VENDOR_DISTANCE_UNIT = "km"

SHUUP_MULTIVENDOR_SHOW_LOG_IN_AS_BUTTON_IN_VENDOR_LIST = True
SHUUP_MULTIVENDOR_SHOW_APPROVAL_BUTTON_IN_VENDOR_LIST = True

SHUUP_ADDRESS_FIELD_PROPERTIES = {
    "email": {"required": True},
    "phone": {"required": True},
    "city": {"required": False},
    "postal_code": {"required": False, "widget": forms.HiddenInput()},
    "street": {"required": False, "widget": forms.HiddenInput()},
    "street2": {"widget": forms.HiddenInput()},
    "name_ext": {"widget": forms.HiddenInput()},
}
SHUUP_FIREBASE_AUTH_ADDRESS_FORM = "givesome.front.forms.address:GivesomeAddressForm"

# Shuup Stripe Multivendor settings
STRIPE_MULTIVENDOR_PAYMENT_MODE = env("STRIPE_MULTIVENDOR_PAYMENT_MODE", default="single-charge")
STRIPE_MULTIVENDOR_CAPTURE_MODE = env("STRIPE_MULTIVENDOR_CAPTURE_MODE", default="auto")

# Shuup Vendor Plans
SHUUP_VENDORS_ENFORCE_SUBSCRIPTION = env("SHUUP_VENDORS_ENFORCE_SUBSCRIPTION", default=False)

# Shuup Stripe Connect
SHUUP_ENFORCE_STRIPE_CONNECT = env("SHUUP_ENFORCE_STRIPE_CONNECT", default=False)

# Shuup API
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "shuup_api.authentication.ExpiringTokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("shuup_api.permissions.ShuupAPIPermission",),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

# Adjust default caches for demos so the bumping get better
# tests. Also ususally with demo there is not enough traffic
# to keep caches up for long time of period. If there is
# nobody browsing for 30 min all caches need to rebuild.
SHUUP_TEMPLATE_HELPERS_CACHE_DURATION = 60 * 420
SHUUP_DEFAULT_CACHE_DURATION = 60 * 420

SHUUP_LOGGING_ENABLE_BASIC_LOGGING = True
SHUUP_LOGGING_SKIP_MENU_ENTRY_URL_NAMES = []
SHUUP_NOTIFY_SCRIPT_RUNNER = "givesome.script_runner.run_event"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

SHUUP_MESSAGES_RECAPTCHA_ENABLED = env.bool("SHUUP_MESSAGES_RECAPTCHA_ENABLED", default=False)
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY", default=None)
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY", default=None)
if SHUUP_MESSAGES_RECAPTCHA_ENABLED and RECAPTCHA_PUBLIC_KEY and RECAPTCHA_PRIVATE_KEY:
    RECAPTCHA_REQUIRED_SCORE = env("RECAPTCHA_REQUIRED_SCORE", default=0.85)
    SHUUP_MESSAGES_USE_RECAPTCHA_V2 = env.bool("SHUUP_MESSAGES_USE_RECAPTCHA_V2", default=True)
    INSTALLED_APPS += ("captcha",)

BASIC_WWW_AUTHENTICATION_USERNAME = env("BASIC_WWW_AUTHENTICATION_USERNAME", default=None)
BASIC_WWW_AUTHENTICATION_PASSWORD = env("BASIC_WWW_AUTHENTICATION_PASSWORD", default=None)
if BASIC_WWW_AUTHENTICATION_USERNAME and BASIC_WWW_AUTHENTICATION_USERNAME:
    BASIC_WWW_AUTHENTICATION = True
    MIDDLEWARE += ("givesome.htaccess_middleware.BasicAuthenticationMiddleware",)

# Project Tracking
SHUUP_SATISMETER_WRITE_KEY = env("SHUUP_SATISMETER_WRITE_KEY", default=("" if DEBUG else "vug9jjO7tigq3wnK"))

sentry_sdk.init(
    env("SENTRY_DSN", default=""), integrations=[DjangoIntegration()], traces_sample_rate=1.0, send_default_pii=True
)

# How many days is a MULTICARD claimed for, when a anonymous user redeems it
GIVESOME_MULTICARD_REDEEM_GRACE_PERIOD_DAYS = 10000  # Disabled for now

CRON_LOG_ROOT = env.str("CRON_LOG_ROOT", default=os.path.join(BASE_DIR, "log"))
CRONJOBS = [
    # ("0 0 * * *", "django.core.management.call_command", ["populate_exchange_rates"]),
]
