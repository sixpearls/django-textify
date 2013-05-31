#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe

from .models import TextifyPost
from .utils import post_type_dict
from django.conf import settings as site_settings
from . import settings
from datetime import datetime
from urlparse import urlparse

class PostTypeMixin(object):
    def get_queryset(self):
        post_type = self.kwargs.get('post_type',settings.POST_TYPES[0][1].__unicode__())
        try:
            queryset = TextifyPost.objects.published().filter(post_type=post_type_dict[post_type])
        except:
            raise Http404
        return queryset

class DateBasedMixin(PostTypeMixin):
    def get_queryset(self):
        year = self.kwargs.get('year','')
        month = self.kwargs.get('month','')
        try:
            month = datetime.strptime(month,'%b').month # 'feb' to 2
        except:
            try:
                month = int(month)
            except:
                month = ''
        day = self.kwargs.get('day','')

        queryset = super(DateBasedMixin,self).get_queryset()

        if year != '':
            queryset = queryset.filter(published__year=year)
        if month != '':
            queryset = queryset.filter(published__month=month)
        if day != '':
            queryset = queryset.filter(published__day=day)
        return queryset

class PostListMixin(object):
    context_object_name = "posts"
    template_name = "textify/post_list.html"
    paginate_by = 10

class PostDatebasedList(DateBasedMixin,PostListMixin,ListView):
    def get_template_names(self):
        return ["textify/post_list_date_based.html", super(PostDatebasedList,self).template_name]

if 'categories' in site_settings.INSTALLED_APPS:
    category_model = TextifyPost._meta.get_field('category').rel.to

    class CategoryBasedMixin(object):
        def get_category_for_path(self,queryset=category_model.objects.all()):
            try:
                self.path
            except:
                path = self.kwargs.get('path',None)
                if path is None:
                    raise Http404
                self.path = path.strip('/').split('/')
            if len(self.path) >= 2:
                for i in range(len(self.path)-1):
                    queryset = queryset.filter(
                        slug__iexact=self.path[-1-i],
                        level=len(self.path)-1-i,
                        parent__slug__iexact=self.path[-2-i])
            else:
                queryset = queryset.filter(
                    slug__iexact=self.path[-1],
                    level=len(self.path) - 1)
            return get_object_or_404(queryset)

        def get_queryset(self):
            try:
                self.category
            except:
                self.category = self.get_category_for_path()
            return TextifyPost.objects.filter(category=self.category)

        def get_context_data(self, **kwargs):
            context = super(CategoryBasedMixin, self).get_context_data(**kwargs)
            query = QueryDict(urlparse(context.get('post_url_querystring','')).query).copy()
            query['category'] = self.kwargs.get('path',None)
            if query['category'] is not None:
                context['post_url_querystring'] = mark_safe('?' + query.urlencode())
            return context

    class PostCategorybasedList(PostListMixin,CategoryBasedMixin,ListView):
        def dispatch(self, request, *args, **kwargs):
            # check if there is some video onsite
            try:
                result = super(PostCategorybasedList, self).dispatch(request, *args, **kwargs)
            except:
                slug = self.path.pop(-1)
                kwargs.update({'slug':slug,'path':'/'.join(self.path)})
                return PostDetail().dispatch(request, *args, **kwargs)
            return result

        def get_template_names(self):
            return ["textify/post_list_category_based.html", super(PostCategorybasedList,self).template_name]
else:
    class CategoryBasedMixin(object):
        pass

if 'taggit' in site_settings.INSTALLED_APPS:
    class TagBasedMixin(object):
        def get_queryset(self):
            tag = self.kwargs.get('tag',None)
            if tag is None:
                raise Http404
            return TextifyPost.objects.filter(tags__name__in=[tag,])

        def get_context_data(self, **kwargs):
            context = super(TagBasedMixin, self).get_context_data(**kwargs)
            query = QueryDict(urlparse(context.get('post_url_querystring','')).query).copy()
            query['tag'] = self.kwargs.get('tag',None)
            if query['tag'] is not None:
                context['post_url_querystring'] = mark_safe('?' + query.urlencode())
            return context

    class PostTagbasedList(PostListMixin,TagBasedMixin,ListView):
        def get_template_names(self):
            return ["textify/post_list_tag_based.html", super(PostTagbasedList,self).template_name]
else:
    class TagBasedMixin(object):
        pass
    

class PostDetail(PostTypeMixin,TagBasedMixin,CategoryBasedMixin,DetailView):
    context_object_name = "post"
    template_name = "textify/post_detail.html"

    def get_queryset(self):
        tag = self.request.GET.get('tag',None)
        category = self.request.GET.get('category',None)
        
        new_kwargs = {'tag': tag, 'path': category}
        new_kwargs.update(self.kwargs)
        self.kwargs = new_kwargs

        if self.kwargs.get('tag',None) or self.kwargs.get('path',None):
            try:
                tag_qs = TagBasedMixin.get_queryset(self)
            except:
                tag_qs = TextifyPost.objects.none()

            try:
                category_qs = CategoryBasedMixin.get_queryset(self)
            except:
                category_qs = TextifyPost.objects.none()

            self.queryset = tag_qs | category_qs
            self.queryset = self.queryset.distinct()
            
        else:
            self.queryset = PostTypeMixin.get_queryset(self)
        
        return self.queryset

    def get_object(self,queryset=None):
        if queryset is None:
            self.get_queryset()
        else:
            self.queryset = queryset
        slug = self.kwargs.get('slug','')
        self.post = get_object_or_404(self.queryset, slug=slug)
        return self.post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['next_post'] = self.get_next_post()
        context['previous_post'] = self.get_previous_post()
        return context

    def get_next_post(self):
        posts = self.queryset
        for index, otherpost in enumerate(posts):
            if otherpost == self.post:
                break
        if (index < (len(posts)-1)):
            return posts[index+1]
        else:
            return None

    def get_previous_post(self):
        posts = self.queryset
        for index, otherpost in enumerate(posts):
            if otherpost == self.post:
                break
        if (index > 0 ):
            return posts[index-1]
        else:
            return None