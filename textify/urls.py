#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url, include
from django.views.generic import date_based

from .views import PostDetail, PostDatebasedList, PostTagbasedList,PostCategorybasedList
from .models import TextifyPost
from . import settings


date_based_patterns = patterns('',

    # post archive index
    url(
        regex  = r'^$',
        view   = PostDatebasedList.as_view(),
        name   = 'post_archive_index'
    ),
    # post archive year list
    url(
        regex  = r'^(?P<year>\d{4})/$',
        view   = PostDatebasedList.as_view(),
        name   = 'post_archive_year'
    ),
    # post archive month list
    url(
        regex  = r'^(?P<year>\d{4})/(?P<month>\w{3})/$',
        view   = PostDatebasedList.as_view(),
        name   = 'post_archive_month_name'
    ),
    # post archive week list
    url(
        regex  = r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        view   = PostDatebasedList.as_view(),
        name   = 'post_archive_month_number'
    ),
    # post archive day list
    url(
        regex  = r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$',
        view   = PostDatebasedList.as_view(),
        name   = 'post_archive_day'
    ),
    url(
        regex  = r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{2})/$',
        view   = PostDatebasedList.as_view(),
        name   = 'post_archive_day_month_number'
    ),
    # post detail
    url(
        regex  = r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<slug>[-\w]+)/$',
        view   =  PostDetail.as_view(),
        name   = 'post_detail',
    ),
    url(
        regex  = r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>[-\w]+)/$',
        view   =  PostDetail.as_view(),
        name   = 'post_detail_month_number',
    ),

)

urlpatterns = patterns('',
    ('^(?P<post_type>\w+)/',include(date_based_patterns)),
)

if 'categories' in settings.settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        ('^category/(?P<path>.+)/$',PostCategorybasedList.as_view()),
    )

if 'taggit' in settings.settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        ('^tag/(?P<tag>\w+)/$',PostTagbasedList.as_view()),
    )