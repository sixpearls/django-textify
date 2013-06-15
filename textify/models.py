#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings as site_settings
from django.db.models.signals import class_prepared
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from django.contrib.sites.models import Site
from django import template
from datetime import datetime

from textify import settings
from textify.utils import load_component


def update_sites_default(sender, **kwargs):
    """
    class_prepared signal handler that checks for the model flatpages.FlatPage
    and adds a default for the 'sites' field
    """
    if sender.__name__ == "FlatPage" and sender._meta.app_label == 'flatpages':
        sender._meta.get_field_by_name('sites')[0].default = [site_settings.SITE_ID]

class_prepared.connect(update_sites_default)

from django.contrib.flatpages.models import FlatPage
if FlatPage._meta.get_field_by_name('sites')[0].default != [site_settings.SITE_ID]:
    update_sites_default(FlatPage)

class TextifyBase(models.Model):
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    content = models.TextField(_('content'), blank=True)
    sites = models.ManyToManyField(Site, default=[site_settings.SITE_ID])

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

def render_content(text,self=None):
    for library in settings.INCLUDE_TAG_LIBRARIES:
        text = "{%% load %s %%}" % library + text

    t = template.Template(text)
    if self is None or not self.pk:
        c = template.Context({'self': None })
    else:
        c = template.Context({'self': self })

    text = t.render(c)

    for renderer, kwargs in settings.RENDERERS:
        text = load_component(renderer)(text,**kwargs)

    return text

class RenderedContentMixin(models.Model):
    content_raw = models.TextField(_('Raw input'), blank=True)

    def save(self, *args, **kwargs):
        self.content = render_content(text=self.content_raw,self=self)
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

class TextifyPageBase(FlatPage,RenderedContentMixin,CommentStatusMixin):

    class Meta:
        abstract = True
        verbose_name = _(u'Textify Page')
        verbose_name_plural = _(u'Textify Pages')

if 'Page' in settings.CONCRETE_MODELS:
    if 'mptt' in site_settings.INSTALLED_APPS:
        from mptt.models import MPTTModel, TreeForeignKey
        class TextifyPage(MPTTModel,TextifyPageBase):
            parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

            class Meta:
                verbose_name = _(u'Textify Page')
                verbose_name_plural = _(u'Textify Pages')

            def get_siblings_include_self(self):
                return self.get_siblings(include_self=True)
    else:
        class TextifyPage(TextifyPageBase):
            class Meta:
                verbose_name = _(u'Textify Page')
                verbose_name_plural = _(u'Textify Pages')

if 'Post' in settings.CONCRETE_MODELS:
    class TextifyPost(TextifyBase,RenderedContentMixin,PublishedItemMixin,CommentStatusMixin):
        post_type = models.IntegerField(_('Post Type'),
            choices=settings.POST_TYPES,
            default=settings.DEFAULT_POST_TYPE)
        if 'categories' in site_settings.INSTALLED_APPS:
            category = models.ForeignKey('categories.Category',blank=True,null=True,on_delete=models.SET_NULL)
        if 'taggit' in site_settings.INSTALLED_APPS:
            tags = TaggableManager(through=TaggedTextifyPost,blank=True)
        if 'massmedia' in site_settings.INSTALLED_APPS:
            featured_image = models.ForeignKey('massmedia.Image',blank=True,null=True,on_delete=models.SET_NULL)
        else:
            featured_image = models.ImageField(upload_to='featured_images/')

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

if 'Chunk' in settings.CONCRETE_MODELS:
    class TextifyChunk(TextifyBase,RenderedContentMixin):
        if 'taggit' in site_settings.INSTALLED_APPS:
            tags = TaggableManager(through=TaggedTextifyChunk,blank=True)

        class Meta:
            verbose_name = _(u'Textify Chunk')
            verbose_name_plural = _(u'Textify Chunks')

    from django import template
    template.add_to_builtins('textify.templatetags.textify_tags')