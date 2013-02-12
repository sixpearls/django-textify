#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from . import settings

def load_component(path):
    """Utily to import a component"""

    if not path:
        return

    idx = path.rfind('.')
    module, attr = path[:idx], path[idx + 1:]

    try:
        mod = import_module(module)
        return getattr(mod, attr)
    except (ImportError, ValueError, AttributeError), e:
        raise ImproperlyConfigured(
            'Error importing component {0}: "{1}"'.format(path, e))

def post_type_dict_function():
    choices_tuple = settings.POST_TYPES
    choices_dict = {}
    for choice in choices_tuple:
        choices_dict[choice[1].__unicode__()] = choice[0]
    return choices_dict

post_type_dict = post_type_dict_function()