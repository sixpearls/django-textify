#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.conf import settings as site_settings
from django.utils.translation import ugettext_lazy as _

from textify import settings
from textify.models import TextifyPage, TextifyPost, TextifyChunk
from textify.forms import TextifyPageForm
from textify.utils import load_component

class RenderedContentAdminMixin(admin.ModelAdmin):
    """ Eventually, this should do magical preview stuff """
    exclude= ['content']

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content_raw':
            kwargs['widget'] = load_component(settings.WIDGET) or forms.Textarea
        return super(RenderedContentAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)

class TextifyPageAdmin(RenderedContentAdminMixin):
    form = TextifyPageForm
    if 'mptt' in site_settings.INSTALLED_APPS:
        fieldsets = (
            (None, {'classes': ('hidden',), 'fields': ('parent__url',)}),
            (None, {'fields': ('title', 'parent', 'url', 'content_raw', 'sites', 'comment_status')}),
            (_('Advanced options'), {'classes': ('collapse',), 'fields': ('registration_required', 'template_name')}),
        )

        fk_prepopulated_fields = {'url': ['parent__url', 'title',]}

        def get_prepopulated_fields(self, request, obj=None):
            """
            Hook for specifying custom prepopulated fields.
            """
            return dict(self.prepopulated_fields.items() + self.fk_prepopulated_fields.items())

        class Media:
            js = ("textify/urlprepopulate.js","admin/js/urlify.js","admin/js/prepopulate.js")
            css = { "all": ("textify/admin.css",) }
    else:
        fieldsets = (
            (None, {'fields': ('url', 'title', 'content_raw', 'sites', 'comment_status')}),
            (_('Advanced options'), {'classes': ('collapse',), 'fields': ('registration_required', 'template_name')}),
        )
    list_display = ('url', 'title')
    list_filter = ('sites', 'comment_status', 'registration_required')
    search_fields = ('url', 'title')

    # if 'mptt' in site_settings.INSTALLED_APPS:
    #     def formfield_for_dbfield(self, db_field, **kwargs):
    #         if db_field.name == 'url':
    #             kwargs['widget'] = urlfield
    #         return super(RenderedContentAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)

class TextifyPostAdmin(RenderedContentAdminMixin):
    #form = TextifyPostForm
    prepopulated_fields = {'slug': ['title',]}
    list_display = ['title', 'modified', 'created', 'published']
    list_filter = ['authors','modified', 'created', 'published']

class TextifyChunkAdmin(RenderedContentAdminMixin):
    #form = TextifyChunkForm
    prepopulated_fields = {'slug': ['title',]}

admin.site.register(TextifyPage, TextifyPageAdmin)
admin.site.register(TextifyPost, TextifyPostAdmin)
admin.site.register(TextifyChunk, TextifyChunkAdmin)