import logging
import re

rec = re.compile
logger = logging.getLogger("engine")

LINK_PATTERN = (
    r"^(https?:\/\/(?:www\.|(?!www))[\w]+[\w]\.[^\s]{2,}|www\.[\w-]+[\w]\.[^\s]{2,})$"
)
LINK_HTML = '<a href="%s">%s</a>'


def parse_link(inline, m, state):
    url = m.group(1)
    return "linkify", url


def render_html_link(url):
    return LINK_HTML % (url, url)


def plugin_linkify(md):
    md.inline.register_rule("linkify", LINK_PATTERN, parse_link)
    md.inline.rules.append("linkify")

    # add HTML renderer
    if md.renderer.NAME == "html":
        md.renderer.register("linkify", render_html_link)
