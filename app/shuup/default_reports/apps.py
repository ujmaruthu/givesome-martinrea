# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.default_reports"
    provides = {
        "reports": [
            "shuup.default_reports.reports.sales:SalesReport",
            "shuup.default_reports.reports.total_sales:TotalSales",
            "shuup.default_reports.reports.sales_per_hour:SalesPerHour",
            "shuup.default_reports.reports.product_total_sales:ProductSalesReport",
            "shuup.default_reports.reports.new_customers:NewCustomersReport",
            "shuup.default_reports.reports.customer_sales:CustomerSalesReport",
            "shuup.default_reports.reports.taxes:TaxesReport",
            "shuup.default_reports.reports.shipping:ShippingReport",
            "shuup.default_reports.reports.refunds.RefundedSalesReport",
            "shuup.default_reports.reports.orders.OrdersReport",
            "shuup.default_reports.reports.orders.OrderLineReport",
        ],
    }
