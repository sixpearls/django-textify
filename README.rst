django-textify
==============

``django-textify`` is a simple CMS that works just the way I like it. Add ``textify`` to your ``INSTALLED_APPS``. Optionally use the following apps::

    categories
    taggit
    markitup
    massmedia
    mediacracy

Textify comes with a number of base models to roll your own text based models. It ships with three concrete models that are used by:

``TextifyPage``
    will drop into ``flatpages`` templates
``TextifyChunk`` 
    is used via the ``textify_tags`` template library
``TextifyPost`` 
    needs ``(r'^',include('textify.urls')),`` added to your ``URLconf``

For more help contact the author, Ben Margolis
