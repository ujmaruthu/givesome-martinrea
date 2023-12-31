# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from ._basket import BasketCampaignForm
from ._basket_conditions import (
    BasketMaxTotalAmountConditionForm,
    BasketMaxTotalProductAmountConditionForm,
    BasketTotalAmountConditionForm,
    BasketTotalProductAmountConditionForm,
    BasketTotalUndiscountedProductAmountConditionForm,
    CategoryProductsBasketConditionForm,
    ChildrenProductConditionForm,
    ContactBasketConditionForm,
    ContactGroupBasketConditionForm,
    HourBasketConditionForm,
    ProductsInBasketConditionForm,
)
from ._basket_effects import (
    BasketDiscountAmountForm,
    BasketDiscountPercentageForm,
    DiscountFromCategoryProductsForm,
    DiscountFromProductForm,
    DiscountPercentageFromUndiscountedForm,
    FreeProductLineForm,
)
from ._catalog import CatalogCampaignForm
from ._catalog_conditions import ContactConditionForm, ContactGroupConditionForm, HourConditionForm
from ._catalog_effects import ProductDiscountAmountForm, ProductDiscountPercentageForm
from ._catalog_filters import CategoryFilterForm, ProductFilterForm, ProductTypeFilterForm
from ._coupon import CouponForm

__all__ = [
    "BasketCampaignForm",
    "BasketDiscountAmountForm",
    "BasketDiscountPercentageForm",
    "BasketMaxTotalAmountConditionForm",
    "BasketMaxTotalProductAmountConditionForm",
    "BasketTotalAmountConditionForm",
    "BasketTotalProductAmountConditionForm",
    "BasketTotalUndiscountedProductAmountConditionForm",
    "CatalogCampaignForm",
    "CategoryFilterForm",
    "CategoryProductsBasketConditionForm",
    "ContactBasketConditionForm",
    "ContactConditionForm",
    "HourConditionForm",
    "HourBasketConditionForm",
    "ContactGroupBasketConditionForm",
    "ContactGroupConditionForm",
    "CouponForm",
    "DiscountFromCategoryProductsForm",
    "DiscountFromProductForm",
    "DiscountPercentageFromUndiscountedForm",
    "FreeProductLineForm",
    "ProductDiscountAmountForm",
    "ProductDiscountPercentageForm",
    "ProductFilterForm",
    "ProductsInBasketConditionForm",
    "ProductTypeFilterForm",
    "ChildrenProductConditionForm",
]
