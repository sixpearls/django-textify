django-textify
==============

``django-textify`` is a simple CMS that works just the way I like it. Add ``textify`` to your ``INSTALLED_APPS``. Optionally use the following apps:

    categories
    taggit
    markitup
    massmedia
    mediacracy

`TextifyPage` will play nicely with `flatpages`, `TextifyChunks` are used via the `textify_tags` template library, and `TextifyPost` needs `(r'^',include('textify.urls')),` added to your `URLconf`. For more help contact the author, Ben Margolis