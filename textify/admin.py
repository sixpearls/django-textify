#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from textify.models import (TextifyPage, TextifyPost, TextifyChunk)
from textify.forms import TextifyPageForm

class RenderedContentAdminMixin(admin.ModelAdmin):
    """ Eventually, this should do magical preview stuff """
    pass

class TextifyPageAdmin(RenderedContentAdminMixin):
    form = TextifyPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content_raw', 'sites', 'comment_status')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'comment_status', 'registration_required')
    search_fields = ('url', 'title')

class TextifyPostAdmin(RenderedContentAdminMixin):
    prepopulated_fields = {'slug': ['title',]}
    list_display = ['title', 'modified', 'created', 'published']
    list_filter = ['authors','modified', 'created', 'published']

class TextifyChunkAdmin(RenderedContentAdminMixin):
    prepopulated_fields = {'slug': ['title',]}

admin.site.register(TextifyPage, TextifyPageAdmin)
admin.site.register(TextifyPost, TextifyPostAdmin)
admin.site.register(TextifyChunk, TextifyChunkAdmin)