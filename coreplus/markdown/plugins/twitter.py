import json
import logging
import re
from urllib import request

esc = re.escape
logger = logging.getLogger("slunic")

# define regex for Twitter links
# https://twitter.com/Linux/status/2311234267
TWITTER_PATTERN = r"http(s)?:\/\/(www)?.?twitter.com\/\w+\/status(es)?\/(?P<uid>([\d]+))(\/)?([^\s]+)?"


def get_tweet(tweet_id):
    """
    Get the HTML code with the embedded tweet.
    It requires an API call at https://api.twitter.com/1/statuses/oembed.json as documented here:
    https://dev.twitter.com/docs/embedded-tweets - section "Embedded Tweets for Developers"
    https://dev.twitter.com/docs/api/1/get/statuses/oembed
    Params:
    tweet_id -- a tweet's numeric id like 2311234267 for the tweet at
    https://twitter.com/Linux/status/2311234267
    """
    try:
        url = "https://api.twitter.com/1/statuses/oembed.json?id={}".format(tweet_id)
        logger.info(f"{tweet_id}, {url}")
        req = request.Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
        res = request.urlopen(req, timeout=3).read()
        data = json.loads(res)
        return data["html"]
    except Exception:
        return ""


# define how to parse matched item
def parse_twitter(inline, m, state):
    # ``inline`` is ``md.inline``, see below
    # ``m`` is matched regex item
    uid = m.group(4)
    return "twitter", uid


# define how to render HTML
def render_html_twitter(uid):
    return '<div class="twitter-wrapper">' + get_tweet(uid) + "</div>"


def plugin_twitter(md):
    # this is an inline grammar, so we register wiki rule into md.inline
    md.inline.register_rule("twitter", TWITTER_PATTERN, parse_twitter)

    # add wiki rule into active rules
    md.inline.rules.append("twitter")

    # add HTML renderer
    if md.renderer.NAME == "html":
        md.renderer.register("twitter", render_html_twitter)
