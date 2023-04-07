import bleach

ALLOWED_ATTRIBUTES = {
    "*": ["class", "style"],
    "a": ["href", "rel"],
    "img": ["src", "alt", "width", "height"],
    "table": ["border", "cellpadding", "cellspacing"],
}

ALLOWED_TAGS = [
    "p",
    "div",
    "br",
    "code",
    "pre",
    "h1",
    "h2",
    "h3",
    "h4",
    "hr",
    "span",
    "s",
    "sub",
    "sup",
    "b",
    "i",
    "img",
    "strong",
    "strike",
    "em",
    "underline",
    "super",
    "table",
    "thead",
    "tr",
    "th",
    "td",
    "tbody",
    "del",
    "details",
    "summary",
]
ALLOWED_TAGS = set(ALLOWED_TAGS).union(bleach.ALLOWED_TAGS)

ALLOWED_PROTOCOLS = ["ftp", "http"]
ALLOWED_PROTOCOLS = set(ALLOWED_PROTOCOLS).union(bleach.ALLOWED_PROTOCOLS)

ALLOWED_STYLES = ["color", "font-weight", "background-color", "width height"]


def embedder(attrs, new, targets=None, embed=None):
    embed = [] if embed is None else embed
    targets = [] if targets is None else targets

    # Existing <a> tag, leave as is.
    if not new:
        return attrs

    href = attrs["_text"]
    linkable = href.startswith(("http", "ftp:", "https"))

    # Don't linkify non http links
    if not linkable:
        return None

    for regex, get_text in targets:
        patt = regex.search(href)
        if patt:
            uid = patt.group("uid")
            obj = get_text(uid)
            embed.append((patt.group(), obj))
            attrs["_text"] = patt.group()
            if "rel" in attrs:
                del attrs["rel"]

    return attrs
