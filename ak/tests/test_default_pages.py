# -*- coding: utf-8 -*-
import pytest
import random


def test_200_page(db, tp):
    """Test a 200 OK page"""

    response = tp.get("ok")
    tp.response_200(response)


def test_403_page(db, tp):
    """Test a 403 error page"""

    response = tp.get("forbidden")
    tp.response_403(response)


def test_404_page(db, tp):
    """Test a 404 error page"""

    rando = random.randint(1000, 20000)
    url = f"/this/should/not/exist/{rando}/"
    response = tp.get(url)
    tp.response_404(response)

    response = tp.get("not_found")
    tp.response_404(response)


def test_500_page(db, tp):
    """Test our 500 error page"""

    url = tp.reverse("internal_server_error")

    # Bail out of this test if this view is not defined
    if not url:
        pytest.skip()

    with pytest.raises(ValueError):
        response = tp.get("internal_server_error")
        print(response.status_code)
