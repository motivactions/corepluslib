# CorePlus Discuss Module

This module handle discussion about related object.

```python
from coreplus import hooks


@hooks.register("API_V1_URL_PATTERNS")
def register_discuss_urls():
    return "discuss/", "coreplus.discuss.api.v1.urls"
```
