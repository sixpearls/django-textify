#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from textify.models import TextifyChunk
from django.core.cache import cache
from django.conf import settings
from random import shuffle

register = template.Library()

CACHE_PREFIX = "textifychunk_"
SLUG_MIDFIX = "slug_"
TAG_MIDFIX = "tag_"

def do_chunk(parser, token):
    tokens = token.split_contents()
    if len(tokens) < 2 or len(tokens) > 3:
        raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s "slug" [ cache_time ] %%}' % (tokens[0],)
    tag_name, slug = tokens
    if len(tokens) == 3:
        cache_time = tokens[2]
    else:
        cache_time = 0
    slug = ensure_quoted_string(slug, "%r tag's slug argument should be in quotes" % tag_name)
    return ChunkNode(slug, cache_time)

class ChunkNode(template.Node):
    def __init__(self, slug, cache_time=0):
       self.slug = slug
       self.cache_time = cache_time

    def render(self, context):
        try:
            cache_key = CACHE_PREFIX + SLUG_MIDFIX + self.slug
            chunk = cache.get(cache_key)
            if chunk is None:
                chunk = TextifyChunk.objects.get(slug=self.slug)
                cache.set(cache_key, chunk, int(self.cache_time))
            content = chunk.content
        except TextifyChunk.DoesNotExist:
            content = ''
        return content


def do_get_chunk(parser, token):
    tokens = token.split_contents()
    if len(tokens) not in (4,5) or tokens[2] != 'as':
        raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s "slug" as varname [ cache_time ] %%}' % tokens[0]
    tagname, slug, varname = tokens[0], tokens[1], tokens[3]
    if len(tokens)==5:
        cache_time = tokens[4]
    else:
        cache_time = 0
    slug = ensure_quoted_string(slug, "Slug argument to %r must be in quotes" % tagname)
    return GetChunkNode(slug, varname, cache_time)

class GetChunkNode(template.Node):
    def __init__(self, slug, varname, cache_time=0):
        self.slug = slug
        self.varname = varname
        self.cache_time = cache_time

    def render(self, context):
        try:
            cache_key = CACHE_PREFIX + SLUG_MIDFIX + self.slug
            chunk = cache.get(cache_key)
            if chunk is None:
                chunk = TextifyChunk.objects.get(slug=self.slug)
                cache.set(cache_key, chunk, int(self.cache_time))
        except TextifyChunk.DoesNotExist:
            chunk = None
        context[self.varname] = chunk
        return ''

if 'taggit' in settings.INSTALLED_APPS:
    def do_get_chunk_by_tag(parser, token):
        tokens = token.split_contents()
        if len(tokens) not in (4,5,6,7) or tokens[2] != 'as' or (len(tokens) in (6,7) and tokens[4] != 'limit'):
            raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s "tag" as varname [ limit num ] [ cache_time ] %%}' % tokens[0]
        tagname, tag, varname = tokens[0], tokens[1], tokens[3]
        if len(tokens) in (6,7):
            limit = tokens[5]
        else:
            limit = None
        if len(tokens)==5:
            cache_time = tokens[4]
        elif len(tokens)==7:
            cache_time = tokens[6]
        else:
            cache_time = 0
        tag = ensure_quoted_string(tag, "Tag argument to %r must be in quotes" % tagname)
        return GetChunkByTagNode(tag, varname, limit, cache_time)

    class GetChunkByTagNode(template.Node):
        def __init__(self,tag,varname,limit=None,cache_time=0):
            self.tag = tag
            self.varname = varname
            self.limit = limit
            self.cache_time = cache_time

        def render(self, context):
            cache_key = CACHE_PREFIX + TAG_MIDFIX + self.tag + '_' + unicode(self.limit)
            chunks = cache.get(cache_key)
            if chunks is None:
                chunks = TextifyChunk.objects.filter(tags__name__in=[self.tag])[:self.limit]
                cache.set(cache_key, chunks, int(self.cache_time))

            chunks = list(chunks)
            shuffle(chunks)

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