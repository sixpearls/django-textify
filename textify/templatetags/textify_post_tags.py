from django import template
from textify.models import TextifyPost
from django.conf import settings
from random import shuffle

register = template.Library()

CACHE_PREFIX = "textifypost_"
SLUG_MIDFIX = "slug_"
TAG_MIDFIX = "tag_"

def do_get_posts(parser, token):
    tokens = token.split_contents()
    if len(tokens)%2 != 1 or tokens[-2] != 'as':
        raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s kw1 arg1 [kw2 arg2 [kw3 arg3 [...]] as varname %%}' % tokens[0]
    kwargs = {tokens[i]: tokens[i+1] for i in range(1,len(tokens)-2, 2) }

    tagname, varname = tokens[0], tokens[-1]
    return GetPostsNode(varname, kwargs)

class GetPostsNode(template.Node):
    def __init__(self, varname, kwargs):
        self.varname = varname
        self.kwargs = kwargs

    def render(self, context):
        kws = dict() # create a new kws dict to render into
        for key in self.kwargs:
            try:
                kws[key] = template.Variable(self.kwargs[key]).resolve(context)
            except template.VariableDoesNotExist:
                kws[key] = self.kwargs[key]
                
        context.update({self.varname: TextifyPost.objects.published().filter(**kws) })
        return ''

def do_get_post(parser, token):
    tokens = token.split_contents()
    if len(tokens)%2 != 1 or tokens[-2] != 'as':
        raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s kw1 arg1 [kw2 arg2 [kw3 arg3 [...]] as varname %%}' % tokens[0]
    kwargs = {tokens[i]: tokens[i+1] for i in range(1,len(tokens)-2, 2) }

    tagname, varname = tokens[0], tokens[-1]
    return GetPostNode(varname, kwargs)

class GetPostNode(template.Node):
    def __init__(self, varname, kwargs):
        self.varname = varname
        self.kwargs = kwargs

    def render(self, context):
        kws = dict() # create a new kws dict to render into
        for key in self.kwargs:
            try:
                kws[key] = template.Variable(self.kwargs[key]).resolve(context)
            except template.VariableDoesNotExist:
                kws[key] = self.kwargs[key]
                
        context.update({self.varname: TextifyPost.objects.published().get(**kws) })
        return ''

register.tag('get_post', do_get_post)

register.tag('get_posts', do_get_posts)