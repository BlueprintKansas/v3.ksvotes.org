# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Registrant


class RefTestCase(TestCase):
    def test_ref_post_external_org(self):
        ref_payload = {
            "name_first": "Foo",
            "name_last": "Bar",
            "email": "foobar@example.com",
        }
        response = self.client.post("/ref?ref=someorg", data=ref_payload)
        sid = self.client.session.get("id")
        registrant = Registrant.lookup_by_session_id(sid)

        self.assertRedirects(response, "/", status_code=302)
        self.assertTrue(sid)
        self.assertEqual(registrant.try_value("name_first"), "Foo")
        self.assertEqual(registrant.ref, "someorg")

    def test_ref_get_with_slash_ok(self):
        response = self.client.get("/ref/?ref=foo")
        self.assertRedirects(response, "/")
        # 'ref' in session but not yet 'id'
        self.assertTrue(self.client.session.get("ref"))
        self.assertFalse(self.client.session.get("id"))
        # session 'ref' should populate form on / page
        response = self.client.get("/")
        self.assertContains(response, "foo")

    def test_ref_post_fails(self):
        response = self.client.post("/ref/")
        self.assertEqual(response.status_code, 404)
