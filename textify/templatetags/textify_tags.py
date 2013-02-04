#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from textify.models import TextifyChunk
from django.core.cache import cache
from django.conf import settings

register = template.Library()

CACHE_PREFIX = "textifychunk_"

def do_chunk(parser, token):
    # split_contents() knows not to split quoted strings.
    tokens = token.split_contents()
    if len(tokens) < 2 or len(tokens) > 3:
        raise template.TemplateSyntaxError, "%r tag should have either 2 or 3 arguments" % (tokens[0],)
    if len(tokens) == 2:
        tag_name, slug = tokens
        cache_time = 0
    if len(tokens) == 3:
        tag_name, slug, cache_time = tokens
    slug = ensure_quoted_string(slug, "%r tag's slug argument should be in quotes" % tag_name)
    return ChunkNode(slug, cache_time)

class ChunkNode(template.Node):
    def __init__(self, slug, cache_time=0):
       self.slug = slug
       self.cache_time = cache_time

    def render(self, context):
        try:
            cache_key = CACHE_PREFIX + self.slug
            c = cache.get(cache_key)
            if c is None:
                c = TextifyChunk.objects.get(slug=self.slug)
                cache.set(cache_key, c, int(self.cache_time))
            content = c.content
        except TextifyChunk.DoesNotExist:
            content = ''
        return content


def do_get_chunk(parser, token):
    tokens = token.split_contents()
    if len(tokens) != 4 or tokens[2] != 'as':
        raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s "slug" as varname %%}' % tokens[0]
    tagname, slug, varname = tokens[0], tokens[1], tokens[3]
    slug = ensure_quoted_string(slug, "Slug argument to %r must be in quotes" % tagname)
    return GetChunkNode(slug, varname)

class GetChunkNode(template.Node):
    def __init__(self, slug, varname):
        self.slug = slug
        self.varname = varname

    def render(self, context):
        try:
            chunk = TextifyChunk.objects.get(slug=self.slug)
        except TextifyChunk.DoesNotExist:
            chunk = None
        context[self.varname] = chunk
        return ''

if 'taggit' in settings.INSTALLED_APPS:
    def do_get_chunk_by_tag(parser, token):
        tokens = token.split_contents()
        if len(tokens) != 4 or tokens[2] != 'as':
            raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s "tag" as varname %%}' % tokens[0]
        tagname, tag, varname = tokens[0], tokens[1], tokens[3]
        tag = ensure_quoted_string(tag, "Tag argument to %r must be in quotes" % tagname)
        return GetChunkByTagNode(tag, varname)

    class GetChunkByTagNode(template.Node):
        def __init__(self,tag,varname):
            self.tag = tag
            self.varname = varname

        def render(self, context):
            chunks = TextifyChunk.objects.filter(tags__name__in=[self.tag])
            context[self.varname] = chunks
            return ''


def ensure_quoted_string(string, error_message):
    '''
    Check to see if the slug is properly double/single quoted and
    returns the string without quotes
    '''
    if not (string[0] == string[-1] and string[0] in ('"', "'")):
        raise template.TemplateSyntaxError, error_message
    return string[1:-1]


register.tag('chunk', do_chunk)
register.tag('get_chunk', do_get_chunk)

if 'taggit' in settings.INSTALLED_APPS:
    register.tag('get_chunk_by_tag', do_get_chunk_by_tag)