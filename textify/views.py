#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.http import require_http_methods

from .models import TextifyPost
from .utils import post_type_dict
from . import settings
from datetime import datetime

class DateBasedMixin(object):
    def get_queryset(self):
        year = self.kwargs.get('year','')
        month = self.kwargs.get('month','')
        try:
            month = datetime.strptime(month,'%b').month # 'feb' to 2
        except:
            pass
        day = self.kwargs.get('day','')
        post_type = self.kwargs.get('post_type',settings.POST_TYPES[0][1].__unicode__())
        try:
            queryset = TextifyPost.objects.filter(post_type=post_type_dict[post_type])
        except:
            raise Http404
        if year != '':
            queryset.filter(published__year=year)
        if month != '':
            queryset.filter(published__month=month)
        if day != '':
            queryset.filter(published__day=day)
        return queryset

class PostDetail(DateBasedMixin,DetailView):
    context_object_name = "post"
    template_name = "textify/post_detail.html"

    def get_object(self):
        slug = self.kwargs.get('slug','')
        return get_object_or_404(self.get_queryset(),slug=slug)

class PostListMixin(object):
    context_object_name = "posts"
    template_name = "textify/post_list.html"
    paginate_by = 10

class PostDatebasedList(DateBasedMixin,PostListMixin,ListView):
    pass

if 'categories' in settings.settings.INSTALLED_APPS:
    category_model = TextifyPost._meta.get_field('category').rel.to

    class PostCategorybasedList(PostListMixin,ListView):
        def get_category_for_path(self,queryset=category_model.objects.all()):
            try:
                path = self.kwargs['path']
            except:
                raise Http404
            path_items = path.strip('/').split('/')
            if len(path_items) >= 2:
                for i in range(len(path_items)-1):
                    queryset = queryset.filter(
                        slug__iexact=path_items[-1-i],
                        level=len(path_items)-1-i,
                        parent__slug__iexact=path_items[-2-i])
            else:
                queryset = queryset.filter(
                    slug__iexact=path_items[-1],
                    level=len(path_items) - 1)
            return get_object_or_404(queryset)

        def get_queryset(self):
            return TextifyPost.objects.filter(category=self.get_category_for_path())

if 'taggit' in settings.settings.INSTALLED_APPS:
    class PostTagbasedList(PostListMixin,ListView):
        def get_queryset(self):
            try:
                tag = self.kwargs['tag']
            except:
                raise Http404
            return TextifyPost.objects.filter(tags__name__in=[tag,])
    