# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


def merged_initial_and_data(form):
    data = {}
    for name, field in form.fields.iteritems():
        data[name] = field.initial
    for source in (form.initial, getattr(form, "cleaned_data", {})):
        for name, value in source.iteritems():
            if value is not None:
                data[name] = value
    return data


def get_effective_form_data(form):
    """
    Return 'effective' data for the form, in essence running its validation methods,
    but trying to return its state to what it was before the `full_clean`. Not fool-
    proof, but what in this universe is.

    :type form: BaseForm
    :return: data dict
    """
    # Stash some attributes
    old = [(key, getattr(form, key)) for key in ("_errors", "_changed_data")]
    form.full_clean()
    data = merged_initial_and_data(form)
    for key, value in old:  # And unstash
        setattr(form, key, value)
    return data


def fill_model_instance(instance, data):
    """
    Fill whatever fields possible in `instance` using the data dict.
    :param instance:
    :param data:
    """
    for field in instance._meta.fields:
        if not field.editable or field.name not in data:
            continue
        field.save_form_data(instance, data[field.name])
    return instance
