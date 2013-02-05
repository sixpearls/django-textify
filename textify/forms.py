#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from textify.models import TextifyPage
from django.contrib.flatpages.forms import FlatpageForm

class TextifyPageForm(FlatpageForm):
    class Meta:
        model = TextifyPage