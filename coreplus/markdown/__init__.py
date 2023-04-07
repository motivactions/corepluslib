import logging

import bleach
import mistune

from .bleaching import ALLOWED_ATTRIBUTES, ALLOWED_PROTOCOLS, ALLOWED_TAGS
from .plugins import gist, twitter, youtube
from .renderer import HTMLRenderer

logger = logging.getLogger("engine")


def safe(f):
    """
    Safely call an object without causing errors
    """

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as exc:
            logger.error(f"Error with {f.__name__}: {exc}")
            text = kwargs.get("text", args[0])
            return text

    return inner


def linkifier(text):

    # List of links to embed
    embed = []

    html = bleach.linkify(
        text=text,
        callbacks=[
            # we can add mention and tag link here
            bleach.callbacks.nofollow,
            bleach.callbacks.target_blank,
        ],
        skip_tags=["pre", "code"],
    )

    # Embed links into html.
    for em in embed:
        source, target = em
        emb = f'<a href="{source}" rel="nofollow">{source}</a>'
        html = html.replace(emb, target)
    return html


@safe
def parse(text, clean=True, escape=False):
    """
    Parses markdown into html.
    Expands certain patterns into HTML.

    clean : Applies bleach clean BEFORE mistune escapes unsafe characters.
            Also removes unbalanced tags at this stage.
    escape  : Escape html originally found in the markdown text.
    allow_rewrite : Serve images with relative url paths from the static directory.
                  eg. images/foo.png -> /static/images/foo.png
    """

    # Bleach clean the html.
    if clean:
        output = bleach.clean(
            text=text,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
        )

    renderer = HTMLRenderer(escape=escape)
    markdown = mistune.create_markdown(
        renderer=renderer,
        escape=escape,
        plugins=[
            gist.plugin_gist,
            twitter.plugin_twitter,
            youtube.plugin_youtube,
            "strikethrough",
            "footnotes",
            "table",
        ],
    )
    output = markdown(output)

    # Embed sensitive links into html
    output = linkifier(text=output)

    return output


@safe
def parse_simple(text, clean=True, escape=False):
    """
    Parses markdown into html.
    Expands certain patterns into HTML.

    clean : Applies bleach clean BEFORE mistune escapes unsafe characters.
            Also removes unbalanced tags at this stage.
    escape  : Escape html originally found in the markdown text.
    """

    # Bleach clean the html.
    if clean:
        output = bleach.clean(
            text=text,
            tags=ALLOWED_TAGS,
            # styles=ALLOWED_STYLES,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
        )

    renderer = HTMLRenderer(escape=escape)
    markdown = mistune.create_markdown(
        renderer=renderer,
        escape=escape,
        plugins=[
            "strikethrough",
            "footnotes",
            "table",
        ],
    )
    output = markdown(output)

    # Embed sensitive links into html
    output = linkifier(text=output)

    return output


def parse_attachment(text, clean=True, escape=True):
    pass
