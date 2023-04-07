# CorePlus Hooks Module

This module add function chaining functionality. By default this module will scan {coreplus.HOOK_FILE_NAME}.py module inside installed django apps. You can use this hook functionality as decorator or a function.

Register hook for `hook_name`. Can be used as a decorator::

```python
from coreplus import hooks

@register('hook_name')
def my_hook(param):
    return f"Formating {param}!"
```

or as a function call:

```python
def my_hook(param):
    return f"Formating {param}!"
register('hook_name', my_hook)
```

and then you can call the hook like so:

```python
from coreplus import hooks

hooked_funcs = hooks.get_hooks("hook_name")
formatted = "hello world"
for func in hooked_funcs:
    formatted = func(formatted)

```
