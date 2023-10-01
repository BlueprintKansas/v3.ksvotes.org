# -*- coding: utf-8 -*-
def test_php_deny(page):
    # all requests that end in .php should be denied
    response = page.goto("/some/path/to/file.php")
    assert response.status == 403
