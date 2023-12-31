#!/bin/bash
set -euxo pipefail

TABLES="""
auth_group
auth_group_permissions
auth_permission
auth_user
auth_user_groups
auth_user_user_permissions
campaigns_basketcampaign
campaigns_basketcampaign_conditions
campaigns_basketcampaign_translation
campaigns_basketcampaignlogentry
campaigns_basketcondition
campaigns_basketdiscountamount
campaigns_basketdiscounteffect
campaigns_basketdiscountpercentage
campaigns_basketlineeffect
campaigns_basketmaxtotalamountcondition
campaigns_basketmaxtotalproductamountcondition
campaigns_baskettotalamountcondition
campaigns_baskettotalproductamountcondition
campaigns_baskettotalundiscountedproductamountcondition
campaigns_catalogcampaign
campaigns_catalogcampaign_conditions
campaigns_catalogcampaign_filters
campaigns_catalogcampaign_translation
campaigns_catalogcampaignlogentry
campaigns_catalogfilter
campaigns_catalogfiltercachedshopproduct
campaigns_categoryfilter
campaigns_categoryfilter_categories
campaigns_categoryproductsbasketcondition
campaigns_categoryproductsbasketcondition_categories
campaigns_categoryproductsbasketcondition_excluded_categories
campaigns_childrenproductcondition
campaigns_contactbasketcondition
campaigns_contactbasketcondition_contacts
campaigns_contactcondition
campaigns_contactcondition_contacts
campaigns_contactgroupbasketcondition
campaigns_contactgroupbasketcondition_contact_groups
campaigns_contactgroupcondition
campaigns_contactgroupcondition_contact_groups
campaigns_contactgroupsalesrange
campaigns_contextcondition
campaigns_coupon
campaigns_couponlogentry
campaigns_couponusage
campaigns_couponusagelogentry
campaigns_discountfromcategoryproducts
campaigns_discountfromproduct
campaigns_discountfromproduct_products
campaigns_discountpercentagefromundiscounted
campaigns_freeproductline
campaigns_freeproductline_products
campaigns_hourbasketcondition
campaigns_hourcondition
campaigns_productdiscountamount
campaigns_productdiscounteffect
campaigns_productdiscountpercentage
campaigns_productfilter
campaigns_productfilter_products
campaigns_productsinbasketcondition
campaigns_productsinbasketcondition_products
campaigns_producttypefilter
campaigns_producttypefilter_product_types
carousel_carousel
carousel_carousel_shops
carousel_slide
carousel_slide_translation
default_tax_taxrule
default_tax_taxrule_customer_tax_groups
default_tax_taxrule_tax_classes
discounts_discount
discounts_discount_happy_hours
discounts_happyhour
discounts_shopproductcatalogdiscountslink
discounts_shopproductcatalogdiscountslink_discounts
discounts_timerange
django_admin_log
django_content_type
django_migrations
django_redirect
django_session
django_site
easy_thumbnails_source
easy_thumbnails_thumbnail
easy_thumbnails_thumbnaildimensions
filer_clipboard
filer_clipboarditem
filer_file
filer_folder
filer_folderpermission
filer_image
filer_thumbnailoption
givesome_completionvideo
givesome_completionvideo_translation
givesome_donationextra
givesome_givecard
givesome_givecardbatch
givesome_givecardcampaign
givesome_givecardcampaign_translation
givesome_givecardpaymentprocessor
givesome_givecardpursecharge
givesome_givesomecompetition
givesome_givesomecompetition_competitors
givesome_givesomedonationdata
givesome_givesomegif
givesome_givesomegroup
givesome_givesomeoffice
givesome_givesomepromotedproduct
givesome_givesomepurse
givesome_givesomepurseallocation
givesome_nullifiedgivecardbatch
givesome_officesustainabilitygoals
givesome_officesustainabilitygoals_goals
givesome_offplatformdonation
givesome_projectextra
givesome_projectsustainabilitygoals
givesome_projectsustainabilitygoals_goals
givesome_purchasereportdata
givesome_receiptingmessages
givesome_receiptingmessages_translation
givesome_supplierofficeterm
givesome_sustainabilitygoal
givesome_sustainabilitygoal_translation
givesome_sustainabilitygoallogentry
givesome_vendorextra
givesome_vendorinformation
givesome_vendorinformation_translation
givesome_vendorsustainabilitygoals
givesome_vendorsustainabilitygoals_goals
givesome_volunteerhours
registration_registrationprofile
registration_supervisedregistrationprofile
reversion_revision
reversion_version
shuup_attribute
shuup_attribute_translation
shuup_attributechoiceoption
shuup_attributechoiceoption_translation
shuup_attributelogentry
shuup_backgroundtask
shuup_backgroundtaskexecution
shuup_basket
shuup_basket_products
shuup_carrier
shuup_carrierlogentry
shuup_category
shuup_category_shops
shuup_category_translation
shuup_category_visibility_groups
shuup_categorylogentry
shuup_cms_blog_blogarticle
shuup_cms_blog_blogarticle_translation
shuup_companycontact
shuup_companycontact_members
shuup_companycontactlogentry
shuup_configurationitem
shuup_contact
shuup_contact_shops
shuup_contactgroup
shuup_contactgroup_members
shuup_contactgroup_translation
shuup_contactgrouplogentry
shuup_contactgrouppricedisplay
shuup_counter
shuup_countrylimitbehaviorcomponent
shuup_currency
shuup_currencylogentry
shuup_customcarrier
shuup_customer_group_pricing_cgpdiscount
shuup_customer_group_pricing_cgpprice
shuup_customertaxgroup
shuup_customertaxgroup_translation
shuup_customertaxgrouplogentry
shuup_custompaymentprocessor
shuup_displayunit
shuup_displayunit_translation
shuup_encryptedconfigurationitem
shuup_favorite_vendors_favoritevendor
shuup_firebase_auth_firebaseuser
shuup_fixedcostbehaviorcomponent
shuup_fixedcostbehaviorcomponent_translation
shuup_front_storedbasket
shuup_front_storedbasket_products
shuup_gdpr_gdprcookiecategory
shuup_gdpr_gdprcookiecategory_block_snippets
shuup_gdpr_gdprcookiecategory_translation
shuup_gdpr_gdprsettings
shuup_gdpr_gdprsettings_consent_pages
shuup_gdpr_gdprsettings_translation
shuup_gdpr_gdpruserconsent
shuup_gdpr_gdpruserconsent_documents
shuup_gdpr_gdpruserconsentdocument
shuup_groupavailabilitybehaviorcomponent
shuup_groupavailabilitybehaviorcomponent_groups
shuup_immutableaddress
shuup_label
shuup_label_translation
shuup_loyalty_card_loyaltycard
shuup_loyalty_card_loyaltycard_orders
shuup_loyalty_card_supplierloyaltysettings
shuup_mailchimp_mailchimpcontact
shuup_mailchimp_mailchimpcontactlogentry
shuup_mailchimp_mailchimpstatuslog
shuup_manufacturer
shuup_manufacturer_shops
shuup_manufacturerlogentry
shuup_mediafile
shuup_mediafile_shops
shuup_mediafolder
shuup_mediafolder_owners
shuup_mediafolder_shops
shuup_messages_message
shuup_messages_messagelogentry
shuup_multicurrencies_display_basecurrency
shuup_multicurrencies_display_currency
shuup_multicurrencies_display_rate
shuup_multicurrencies_display_ratesource
shuup_multicurrencies_display_userpreferredcurrency
shuup_multivendor_containssupplierbehaviorcomponent
shuup_multivendor_locationopeningperiod
shuup_multivendor_multivendorproduct
shuup_multivendor_multivendorproduct_managers
shuup_multivendor_ordergroup
shuup_multivendor_ordergroupitem
shuup_multivendor_orderlinesupplierlocation
shuup_multivendor_productapproval
shuup_multivendor_productapprovalcomment
shuup_multivendor_productapprovalcomment_translation
shuup_multivendor_productapprovalhistorymanager
shuup_multivendor_productsupplierlocation
shuup_multivendor_supplierlocation
shuup_multivendor_supplierorder
shuup_multivendor_supplierprice
shuup_multivendor_supplieruser
shuup_multivendor_vendorcategory
shuup_multivendor_vendorcategory_translation
shuup_multivendor_vendorcategory_vendors
shuup_multivendor_vendorcontactdistance
shuup_multivendor_vendorextra
shuup_multivendor_vendorextra_consented_documents
shuup_multivendor_vendorfunds
shuup_multivendor_vendormedia
shuup_multivendor_vendormedia_translation
shuup_multivendor_vendormedialogentry
shuup_multivendor_vendororderlinerevenue
shuup_multivendor_vendorprimarycategory
shuup_mutableaddress
shuup_notify_emailtemplate
shuup_notify_notification
shuup_notify_script
shuup_notify_scriptlogentry
shuup_opening_hours_supplieravailableforordersperiod
shuup_opening_hours_supplieropeningperiod
shuup_order
shuup_order_customer_groups
shuup_orderline
shuup_orderline_labels
shuup_orderlinelogentry
shuup_orderlinetax
shuup_orderlinetaxlogentry
shuup_orderlogentry
shuup_orderstatus
shuup_orderstatus_allowed_next_statuses
shuup_orderstatus_translation
shuup_orderstatushistory
shuup_ordertotallimitbehaviorcomponent
shuup_payment
shuup_paymentlogentry
shuup_paymentmethod
shuup_paymentmethod_behavior_components
shuup_paymentmethod_labels
shuup_paymentmethod_translation
shuup_paymentmethodlogentry
shuup_paymentprocessor
shuup_paymentprocessorlogentry
shuup_paypal_capture_paypalauthorizeandcapture
shuup_persistentcacheentry
shuup_personcontact
shuup_personcontactlogentry
shuup_product
shuup_product_comparison_comparableattribute
shuup_product_modifier_orderlineproductmodifiers
shuup_product_modifier_orderlineproductmodifiers_modifiers
shuup_product_modifier_productmodifier
shuup_product_modifier_productmodifier_translation
shuup_product_modifier_productmodifierclass
shuup_product_modifier_productmodifierclass_translation
shuup_product_modifier_productmodifierlink
shuup_product_modifier_productmodifierlink_classes
shuup_product_reviews_productreview
shuup_product_reviews_productreviewaggregation
shuup_product_translation
shuup_productattribute
shuup_productattribute_chosen_options
shuup_productattribute_translation
shuup_productcatalogdiscountedprice
shuup_productcatalogdiscountedpricerule
shuup_productcatalogprice
shuup_productcatalogpricerule
shuup_productcrosssell
shuup_productlogentry
shuup_productmedia
shuup_productmedia_shops
shuup_productmedia_translation
shuup_productmedialogentry
shuup_productpackagelink
shuup_producttype
shuup_producttype_attributes
shuup_producttype_translation
shuup_productvariationresult
shuup_productvariationvariable
shuup_productvariationvariable_translation
shuup_productvariationvariablevalue
shuup_productvariationvariablevalue_translation
shuup_rewards_multivendor_orderlinerewardadjustment
shuup_rewards_multivendor_rewardadjustment
shuup_rewards_multivendor_rewardcount
shuup_rewards_multivendor_rewardsproductconfiguration
shuup_salesunit
shuup_salesunit_translation
shuup_savedaddress
shuup_savedaddresslogentry
shuup_sent_emails_sentemail
shuup_servicebehaviorcomponent
shuup_serviceprovider
shuup_serviceprovider_shops
shuup_serviceprovider_translation
shuup_shipment
shuup_shipmentlogentry
shuup_shipmentproduct
shuup_shipmentproductlogentry
shuup_shippingmethod
shuup_shippingmethod_behavior_components
shuup_shippingmethod_labels
shuup_shippingmethod_translation
shuup_shippingmethodlogentry
shuup_shippo_multivendor_shippobehaviorcomponent
shuup_shippo_multivendor_shippocarrieraccount
shuup_shippo_multivendor_shippomultivendorcarrier
shuup_shippo_multivendor_shippoorder
shuup_shippo_multivendor_shipposhipmentdetails
shuup_shop
shuup_shop_labels
shuup_shop_staff_members
shuup_shop_translation
shuup_shoplogentry
shuup_shopproduct
shuup_shopproduct_categories
shuup_shopproduct_payment_methods
shuup_shopproduct_shipping_methods
shuup_shopproduct_suppliers
shuup_shopproduct_translation
shuup_shopproduct_visibility_groups
shuup_shopproductlogentry
shuup_simple_cms_page
shuup_simple_cms_page_available_permission_groups
shuup_simple_cms_page_translation
shuup_simple_cms_pagelogentry
shuup_simple_cms_pageopengraph
shuup_simple_cms_pageopengraph_translation
shuup_smtpaccount
shuup_staffonlybehaviorcomponent
shuup_stripe_multivendor_commissioninvoice
shuup_stripe_multivendor_commissioninvoiceorder
shuup_stripe_multivendor_commissioninvoiceorder_from_orders
shuup_stripe_multivendor_paymentmethodtodetach
shuup_stripe_multivendor_paymentmethodwebhook
shuup_stripe_multivendor_paymentprocessorwebhook
shuup_stripe_multivendor_stripeconnectedaccount
shuup_stripe_multivendor_stripeconnectedcustomer
shuup_stripe_multivendor_stripeconnectedpaymentmethod
shuup_stripe_multivendor_stripeconnectedsupplieraccount
shuup_stripe_multivendor_stripecustomer
shuup_stripe_multivendor_stripecustomsupplierfees
shuup_stripe_multivendor_stripeinvoice
shuup_stripe_multivendor_stripeinvoiceline
shuup_stripe_multivendor_stripemultivendorpaymentprocessor
shuup_stripe_multivendor_stripepayment
shuup_stripe_multivendor_stripeproduct
shuup_stripe_multivendor_striperefund
shuup_stripe_multivendor_stripetransfer
shuup_stripe_multivendor_stripevendorcustomer
shuup_stripe_multivendor_stripewebhook
shuup_stripe_subscriptions_invoice
shuup_stripe_subscriptions_invoiceline
shuup_stripe_subscriptions_stripecustomer
shuup_stripe_subscriptions_stripecustomersubscription
shuup_stripe_subscriptions_stripeplan
shuup_stripe_subscriptions_stripeprice
shuup_stripe_subscriptions_stripeproduct
shuup_stripe_subscriptions_stripesubscription
shuup_stripe_subscriptions_stripesubscriptionpaymentprocessor
shuup_stripe_subscriptions_webhookeventlogentry
shuup_subscriptions_invoice
shuup_subscriptions_invoiceline
shuup_subscriptions_invoicepayment
shuup_subscriptions_invoicerefundline
shuup_subscriptions_plan
shuup_subscriptions_plan_products
shuup_subscriptions_plan_suppliers
shuup_subscriptions_plan_translation
shuup_subscriptions_subscription
shuup_subscriptions_subscriptionpayment
shuup_subscriptions_subscriptionproductsonlycomponent
shuup_subscriptions_subscriptionshipment
shuup_suppliedproduct
shuup_suppliedproductlogentry
shuup_supplier
shuup_supplier_supplier_modules
shuup_supplier_translation
shuup_supplierlogentry
shuup_suppliermodule
shuup_suppliershop
shuup_tasks_task
shuup_tasks_taskcomment
shuup_tasks_tasklogentry
shuup_tasks_tasktype
shuup_tasks_tasktype_translation
shuup_tax
shuup_tax_translation
shuup_taxclass
shuup_taxclass_translation
shuup_taxclasslogentry
shuup_taxlogentry
shuup_testing_carrierwithcheckoutphase
shuup_testing_expensiveswedenbehaviorcomponent
shuup_testing_fieldsmodel
shuup_testing_paymentwithcheckoutphase
shuup_testing_pseudopaymentprocessor
shuup_testing_supplierprice
shuup_testing_ultrafilter
shuup_testing_ultrafilter_categories
shuup_testing_ultrafilter_product_types
shuup_testing_ultrafilter_products
shuup_testing_ultrafilter_shop_products
shuup_typography_fontfamily
shuup_vendor_plans_cancellationinfo
shuup_vendor_plans_planvendorvisilibity
shuup_vendor_plans_planvendorvisilibity_vendors
shuup_vendor_reviews_vendorreview
shuup_vendor_reviews_vendorreviewaggregation
shuup_vendor_reviews_vendorreviewoption
shuup_vendor_reviews_vendorreviewoption_translation
shuup_waivingcostbehaviorcomponent
shuup_waivingcostbehaviorcomponent_translation
shuup_weightbasedpricerange
shuup_weightbasedpricerange_translation
shuup_weightbasedpricingbehaviorcomponent
shuup_weightlimitsbehaviorcomponent
shuup_wishlist_wishlist
shuup_wishlist_wishlist_products
shuup_xtheme_adminthemesettings
shuup_xtheme_font
shuup_xtheme_savedviewconfig
shuup_xtheme_snippet
shuup_xtheme_themesettings
simple_supplier_stockadjustment
simple_supplier_stockcount
"""

#gcloud sql databases delete gsqa --instance=givesomeappdb
echo "Deleting old QA database..."
PGPASSWORD=${GIVESOME_ROOT_USER_POSTGRES_PASS} psql \
    -U postgres \
    -h 34.122.0.74 \
    -p 5432 \
    -c 'DROP DATABASE gsqa;'

PGPASSWORD=${GIVESOME_ROOT_USER_POSTGRES_PASS} psql \
    -U postgres \
    -h 34.122.0.74 \
    -p 5432 \
    -c 'CREATE DATABASE gsqa TEMPLATE gsa;'

PGPASSWORD=${GIVESOME_ROOT_USER_POSTGRES_PASS} psql \
    -U postgres \
    -h 34.122.0.74 \
    -p 5432 \
    -c 'GRANT ALL PRIVILEGES ON DATABASE gsqa TO givesomeqauser;'

PGPASSWORD=${GIVESOME_ROOT_USER_POSTGRES_PASS} psql \
    -U postgres \
    -h 34.122.0.74 \
    -p 5432 \
    -c 'GRANT ALL PRIVILEGES ON DATABASE gsqa TO cloudsqlsuperuser;'

for table in $TABLES
  do
    ALTER_TABLE_COMMAND="$ALTER_TABLE_COMMAND ALTER TABLE public.$table OWNER TO givesomeqauser;"
done

PGPASSWORD=${GIVESOME_APP_USER_POSTGRES_PASS} psql \
    -U givesomeappuser \
    -h 34.122.0.74 \
    -p 5432 gsqa <<EOF
$ALTER_TABLE_COMMAND
EOF


# Below are not valid credentials / these are testing keys
PGPASSWORD=${GIVESOME_QA_USER_POSTGRES_PASS} psql \
    -U givesomeqauser \
    -h 34.122.0.74 \
    -p 5432 \
    gsqa \
    -c "UPDATE shuup_stripe_multivendor_stripemultivendorpaymentprocessor SET publishable_key = 'MwcUIc9QoY8koIHjYHve3bFT6qIwHOOFHDKq05o6DH8jXg1McZvbIYK7W_JaLi8m', secret_key='oUTDyGDuEk_S9LvZj-K35e_FF_wpSm49F9p1iH6d3xFKCqVJKJpWLWnjfZxi2aFY' WHERE paymentprocessor_ptr_id = 2;"

gsutil -m rsync -r gs://givesome-application-media/ gs://givesome-application-media-qa/
