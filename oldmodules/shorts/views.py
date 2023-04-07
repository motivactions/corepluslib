# views.py
from django.http import Http404
from django.shortcuts import render

from .models import ShortUrl

template = "redirect.html"


def redirect_view(request, shortened_part):
    # TODO Visitor count per ip/day
    # TODO Rate limiting
    try:
        shortener = ShortUrl.objects.get(
            url_shortened=shortened_part,
            is_active=True,
        )
        shortener.visitor += 1
        shortener.save()
        context = {"url_path": shortener.url_original}
        return render(request, template, context)
    except shortener.DoesNotExist:
        raise Http404("Sorry this link is broken :(")
