# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib.auth import get_user_model
from typing import Iterable, Union

from shuup.apps.provides import get_provide_objects
from shuup.core.models import Product, Shop, Supplier
from shuup.core.pricing import TaxfulPrice, TaxlessPrice

UserModel = get_user_model()


class ProductSubscriptionOption:
    value = None
    label = None
    price = None
    description = None

    def __init__(self, label: str, value: str, price: Union[TaxfulPrice, TaxlessPrice], description: str = None):
        self.label = label
        self.value = value
        self.price = price
        self.description = description


class ProductSubscriptionContext:
    shop = None
    product = None
    supplier = None
    user = None

    def __init__(self, shop: Shop, product: Product, supplier: Supplier = None, user: UserModel = None, **kwargs):
        self.shop = shop
        self.product = product
        self.supplier = supplier
        self.user = user


class BaseProductSubscriptionOptionProvider:
    @classmethod
    def get_subscription_options(cls, context: ProductSubscriptionContext) -> Iterable[ProductSubscriptionOption]:
        raise NotImplementedError()


def get_product_subscription_options(
    context: ProductSubscriptionContext, **kwargs
) -> Iterable[ProductSubscriptionOption]:
    for product_subscription_option_provider in get_provide_objects("product_subscription_option_provider"):
        if not issubclass(product_subscription_option_provider, BaseProductSubscriptionOptionProvider):
            continue

        yield from product_subscription_option_provider.get_subscription_options(context)
