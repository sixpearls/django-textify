#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
# from django.views.generic import date_based

from .views import PostDetail, PostDatebasedList
from .models import TextifyPost
from django.conf import settings


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
        regex  = r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<slug>[-_\w]+)/$',
        view   =  PostDetail.as_view(),
        name   = 'post_detail',
    ),
    url(
        regex  = r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>[-_\w]+)/$',
        view   =  PostDetail.as_view(),
        name   = 'post_detail_month_number',
    ),
    url(
        regex  = r'^(?P<year>\d{4})/(?P<slug>[-_\w]+)/$',
        view   =  PostDetail.as_view(),
        name   = 'post_detail_year_only',
    ),

)

urlpatterns = patterns('',
    ('^(?P<post_type>\w+)/',include(date_based_patterns)),
)

if 'categories' in settings.INSTALLED_APPS:
    from .views import PostCategorybasedList
    urlpatterns += patterns('',
        url(
            regex = r'^category/(?P<path>.+)/$',
            view = PostCategorybasedList.as_view(),
            name = "post_by_category"),
    )

if 'taggit' in settings.INSTALLED_APPS:
    from .views import PostTagbasedList
    urlpatterns += patterns('',
        url( 
            regex = r'^tag/(?P<tag>[-_\w]+)/$',
            view = PostTagbasedList.as_view(),
            name = "post_by_tag"),
        url(
            regex = r'^tag/(?P<tag>[-_\w]+)/(?P<slug>[-_\w]+)/$',
            view = PostDetail.as_view(),
            name = "post_detail_tag"),
    )