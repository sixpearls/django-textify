#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

DEFAULT_PUBLISH_STATUS_CHOICES = (
    (1, _(u'DRAFT')),
    (2, _(u'PRIVATE')),
    (3, _(u'PUBLISHED')),
)

DEFAULT_PUBLISH_STATUS_TEST = Q(publish_status__gt=2)

DEFAULT_COMMENT_STATUS_CHOICES = (
    (0, _('Comments Disabled')),
    (1, _('Comments Enabled')),
    (2, _('Comments Frozen'))
)

DEFAULT_POST_TYPES = (
    (1, _(u'blog')),
    (2, _(u'article')),
    (3, _(u'story')),
)

DEFAULT_SETTINGS = {
    'AUTHOR_MODEL': 'auth.User',
    'AUTHOR_MODEL_LIMIT': None,
    'PUBLISH_STATUS_CHOICES': DEFAULT_PUBLISH_STATUS_CHOICES,
    'PUBLISH_STATUS_TEST': DEFAULT_PUBLISH_STATUS_TEST,
    'DEFAULT_PUBLISH_STATUS': 1,
    'COMMENT_STATUS_CHOICES': DEFAULT_COMMENT_STATUS_CHOICES,
    'DEFAULT_COMMENT_STATUS': 1,
    'POST_TYPES': DEFAULT_POST_TYPES,
    'DEFAULT_POST_TYPE': 1,
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'TEXTIFY_SETTINGS', {}))

globals().update(USER_SETTINGS)
