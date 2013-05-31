#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings as site_settings
from textify.models import TextifyPage
from django.contrib.flatpages.forms import FlatpageForm

class TextifyPageForm(FlatpageForm):
    if 'mptt' in site_settings.INSTALLED_APPS:
        parent__url = forms.Field() 
        # to make this generic, the followed field would need to be added by a class generator/modifier

        def __init__(self,*args,**kwargs):
            super(TextifyPageForm,self).__init__(*args,**kwargs)

            CHOICES_TUPLE = tuple( (url, unicode(pk)) for pk,url in self.fields["parent"].queryset.values_list('id','url') )
            self.fields["parent__url"] = forms.ChoiceField(choices=CHOICES_TUPLE)
            # the specific translation tuple would also need to be meta-generated

        def __getitem__(self,name):
            if name == 'parent__url': # a generic "__" in name test, to be generic
                try:
                    bf = super(TextifyPageForm,self).__getitem__(name) 
                    # grab the bound field of the generated followed field
                    try:
                        bf.original_field = super(TextifyPageForm,self).__getitem__("parent")
                        # grab the bound field of the FK with the parameter we want
                    except:
                        raise
                    else:
                        return bf
                except:
                    raise
            elif name == 'url': 
                # the metaclass would need to get information from the Admin to know which fields are prepopulated by
                # following an FK
                bf = super(TextifyPageForm,self).__getitem__(name)
                bf.follows_fk = True # set a flag on the BF that can be accessed by admin's template tag
                return bf
            else:
                return super(TextifyPageForm,self).__getitem__(name)

    class Meta:
        model = TextifyPage