# CorePlus Navigators Module

This is navigations and menu management module.

```python

def init_app(sender, **kwargs):
    """Create initial main navigation menu"""
    from coreplus.navigators.models import Menu, Placeholder

    for nav in Placeholder.objects.all():
        nav.delete()

    for menu in Menu.objects.all():
        menu.delete()

    # create menu top root
    try:
        main_menu = Menu.objects.get(slug="top-menu")
    except Menu.DoesNotExist:
        main_menu = Menu(
            url="/",
            label="Top Menu",
            slug="top-menu",
        )
        main_menu.save()

    # create menu home
    try:
        home_menu = Menu.objects.get(slug="top-home")
    except Menu.DoesNotExist:
        home_menu = Menu(
            url="/",
            label="Home",
            slug="top-home",
            parent=main_menu,
        )
        home_menu.save()

    # services menu
    try:
        services_menu = Menu.objects.get(slug="community")
    except Menu.DoesNotExist:
        services_menu = Menu(
            url="/community/",
            label="Communities",
            slug="community",
            parent=main_menu,
        )
        services_menu.save()

    # articles menu
    try:
        blog_menu = Menu.objects.get(slug="docs")
    except Menu.DoesNotExist:
        blog_menu = Menu(
            url="/docs/",
            label="Documentation",
            slug="docs",
            parent=main_menu,
        )
        blog_menu.save()

    # contacts menu
    try:
        contact_menu = Menu.objects.get(slug="top-contacts")
    except Menu.DoesNotExist:
        contact_menu = Menu(
            url="/contacts/",
            label="Get in Touch",
            slug="top-contacts",
            parent=main_menu,
        )
        contact_menu.save()

    try:
        main_nav = Placeholder.objects.get(slug="top-navigation")
    except Placeholder.DoesNotExist:
        main_nav = Placeholder(
            name="Top Placeholder",
            slug="top-navigation",
            menu_root=main_menu,
        )
        main_nav.save()
```
