#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from textify.models import TextifyPage, TextifyPost, TextifyChunk
from textify.forms import TextifyPageForm

from markitup.widgets import AdminMarkItUpWidget

class TextifyMarkitupAdminWidget(AdminMarkItUpWidget):
    def _media(self):
        return super(TextifyMarkitupAdminWidget,self).media + forms.Media(js=("textify/markitup/constant_preview_refresh.js",))
    media = property(_media)


class RenderedContentAdminMixin(admin.ModelAdmin):
    """ Eventually, this should do magical preview stuff """
    exclude= ['content']

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content_raw':
            kwargs['widget'] = TextifyMarkitupAdminWidget()
        return super(RenderedContentAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)

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