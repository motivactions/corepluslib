from django.test import TestCase, tag

from coreplus import markdown

TEST_INPUT1 = """

## Test render link
https://www.coreplus.co.id/p/1 https://www.coreplus.co.id/p/2
http://localhost:8000/p/3/
http://localhost:8000/accounts/profile/5

## Test render mention

@test

## Test render tag

#testtag1 #testtag2

## Test blockcode

```
print 123
http://www.psu.edu
```

## Test Youtube embed
https://www.youtube.com/watch?v=Hc8QdwfYFT8


## Test twitter embed
https://twitter.com/Linux/status/2311234267

## Test Gist embed
https://gist.github.com/justsasri/a23c13b7d6e5a46f473a4f57673e9970#file-greet-py
"""

TEST_INPUT2 = """
http://test.coreplus.co.id/accounts/profile/user-2/
http://test.coreplus.co.id/p/p371285/
"""


class MarkdownTestCase(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    @tag("markdown_unit_test")
    def test_markdown_parse(self):
        results = markdown.parse(TEST_INPUT1)
        return results
