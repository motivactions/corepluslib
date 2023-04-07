import logging
import re

rec = re.compile
logger = logging.getLogger("engine")

# Youtube patterns
# https://www.youtube.com/watch?v=G7RDn8Xtf_Y
YOUTUBE_PATTERN1 = r"http(s)?:\/\/www.youtube.com\/watch\?v=(?P<uid>([\w-]+))(\/)?"
YOUTUBE_PATTERN2 = r"https:\/\/www.youtube.com\/embed\/(?P<uid>([\w-]+))(\/)?"
YOUTUBE_PATTERN3 = r"https:\/\/youtu.be\/(?P<uid>([\w-]+))(\/)?"

YOUTUBE_HTML = (
    '<div class="ratio ratio-16x9">'
    '<iframe src="//www.youtube.com/embed/%s" allowfullscreen></iframe>'
    "</div>"
)


def parse_youtube1(inline, m, state):
    uid = m.group(2)
    return "youtube1", uid


def parse_youtube2(inline, m, state):
    uid = m.group(2)
    return "youtube1", uid


def parse_youtube3(inline, m, state):
    uid = m.group(2)
    return "youtube3", uid


def render_html_youtube(uid):
    return YOUTUBE_HTML % uid


def plugin_youtube(md):
    md.inline.register_rule("youtube1", YOUTUBE_PATTERN1, parse_youtube1)
    md.inline.register_rule("youtube2", YOUTUBE_PATTERN2, parse_youtube2)
    md.inline.register_rule("youtube3", YOUTUBE_PATTERN3, parse_youtube3)
    md.inline.rules.append("youtube1")
    md.inline.rules.append("youtube2")
    md.inline.rules.append("youtube3")

    if md.renderer.NAME == "html":
        md.renderer.register("youtube1", render_html_youtube)
        md.renderer.register("youtube2", render_html_youtube)
        md.renderer.register("youtube3", render_html_youtube)
