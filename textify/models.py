#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings as site_settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django import template
from datetime import datetime

from textify import settings
from textify.utils import load_component

class TextifyBase(models.Model):
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    content = models.TextField(_('content'), blank=True)
    sites = models.ManyToManyField(Site)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s' % self.title

class PublishedItemsManager(models.Manager):
    """Returns published posts that are not in the future."""
    def published(self):
        return self.get_query_set().filter(
            settings.PUBLISH_STATUS_TEST).filter(
            published__isnull=False).filter(
            published__lte=datetime.now()).order_by('-published')

class PublishedItemMixin(models.Model):
    description = models.TextField(_('description'),blank=True)
    authors = models.ManyToManyField(
        settings.AUTHOR_MODEL,
        verbose_name=_('authors'),
        blank=True,
        null=True,
        limit_choices_to=settings.AUTHOR_MODEL_LIMIT)

    created = models.DateTimeField(_('created'),auto_now_add=True)
    modified = models.DateTimeField(_('modified'),auto_now=True)

    published = models.DateTimeField(_('published'), default=datetime.now, blank=True, null=True)
    publish_status = models.IntegerField(_('Publish status'),
        choices=settings.PUBLISH_STATUS_CHOICES,
        default=settings.DEFAULT_PUBLISH_STATUS)
    objects = PublishedItemsManager()

    class Meta:
        abstract = True
        ordering = ['-published']

class CommentStatusMixin(models.Model):
    comment_status = models.IntegerField(_('Comment Status'),
        choices=settings.COMMENT_STATUS_CHOICES,
        default=settings.DEFAULT_COMMENT_STATUS
    )

    class Meta:
        abstract = True

def render_content(text):
    for renderer, kwargs in settings.RENDERERS:
        text = load_component(renderer)(text,**kwargs)
    for library in settings.INCLUDE_TAG_LIBRARIES:
        text = "{%% load %s %%}" % library + text
    t = template.Template(text)
    c = template.Context({})
    return t.render(c)

class RenderedContentMixin(models.Model):
    content_raw = models.TextField(_('Raw input'), blank=True)

    def save(self, *args, **kwargs):
        self.content = render_content(self.content_raw)
        super(RenderedContentMixin,self).save(*args,**kwargs)

    @property
    def safe_content(self):
        return mark_safe(self.content)

    class Meta:
        abstract = True

if 'taggit' in site_settings.INSTALLED_APPS:
    from taggit.managers import TaggableManager
    from taggit.models import ItemBase,TagBase,TaggedItemBase

    class TextifyPostTag(TagBase):
        class Meta:
            verbose_name = _("Post Tag")
            verbose_name_plural = _("Post Tags")

    class TextifyChunkTag(TagBase):
        class Meta:
            verbose_name = _("Chunk Tag")
            verbose_name_plural = _("Chunk Tags")

    class TaggedTextifyPost(ItemBase):
        content_object = models.ForeignKey('TextifyPost')
        tag = models.ForeignKey(TextifyPostTag, related_name="items")

        tags_for = classmethod(TaggedItemBase.tags_for.im_func)

    class TaggedTextifyChunk(ItemBase):
        content_object = models.ForeignKey('TextifyChunk')
        tag = models.ForeignKey(TextifyChunkTag, related_name="items")

        tags_for = classmethod(TaggedItemBase.tags_for.im_func)

class TextifyPage(FlatPage,RenderedContentMixin,CommentStatusMixin):
    class Meta:
        verbose_name = _(u'Textify Page')
        verbose_name_plural = _(u'Textify Pages')

class TextifyPost(TextifyBase,RenderedContentMixin,PublishedItemMixin,CommentStatusMixin):
    post_type = models.IntegerField(_('Post Type'),
        choices=settings.POST_TYPES,
        default=settings.DEFAULT_POST_TYPE)
    if 'categories' in site_settings.INSTALLED_APPS:
        category = models.ForeignKey('categories.Category',blank=True,null=True)
    if 'taggit' in site_settings.INSTALLED_APPS:
        tags = TaggableManager(through=TaggedTextifyPost,blank=True)
    if 'massmedia' in site_settings.INSTALLED_APPS:
        featured_image = models.ForeignKey('massmedia.Image',blank=True,null=True)
    else:
        featured_image = models.ImageField()

    class Meta(PublishedItemMixin.Meta):
        verbose_name = _(u'Textify Post')
        verbose_name_plural = _(u'Textify Posts')

    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), {
            'post_type': self.get_post_type_display(),
            'year': self.published.year,
            'month': self.published.strftime('%b').lower(),
            'slug': self.slug
        })

class TextifyChunk(TextifyBase,RenderedContentMixin):
    if 'taggit' in site_settings.INSTALLED_APPS:
        tags = TaggableManager(through=TaggedTextifyChunk,blank=True)

    class Meta:
        verbose_name = _(u'Textify Chunk')
        verbose_name_plural = _(u'Textify Chunks')

from django import template
template.add_to_builtins('textify.templatetags.textify_tags')