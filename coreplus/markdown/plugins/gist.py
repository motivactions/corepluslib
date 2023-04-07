import logging
import re

rec = re.compile
logger = logging.getLogger("engine")

# define regex for Gist links
# https://gist.github.com/justsasri/a23c13b7d6e5a46f473a4f57673e9970#file-greet-py
GIST_PATTERN = r"https:\/\/gist.github.com\/(?P<uid>([\w\/]+))"
GIST_HTML = '<script src="https://gist.github.com/%s.js"></script>'


# define how to parse matched item
def parse_gist(inline, m, state):
    # ``inline`` is ``md.inline``, see below
    # ``m`` is matched regex item
    uid = m.group(2)
    return "gist", uid


# define how to render HTML
def render_html_gist(uid):
    return GIST_HTML % uid


def plugin_gist(md):
    # this is an inline grammar, so we register wiki rule into md.inline
    md.inline.register_rule("gist", GIST_PATTERN, parse_gist)

    # add wiki rule into active rules
    md.inline.rules.append("gist")

    # add HTML renderer
    if md.renderer.NAME == "html":
        md.renderer.register("gist", render_html_gist)
