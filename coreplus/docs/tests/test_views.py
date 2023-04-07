import os
from importlib import reload

from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase, tag
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

from coreplus.docs import views

TEST_DOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_docs"))


class DocsViewsTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.rf = RequestFactory()
        self.user = User(username="testuser")
        self.staff = User(username="teststaff")
        self.admin = User(username="testadmin")
        self.user.set_password("123")
        self.staff.set_password("123")
        self.admin.set_password("123")
        reload(views)


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS="wrong-value")
class IncorrectAccessTest(DocsViewsTestBase):
    @tag("coreplus_docs_unit_testing")
    def test_docs_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertNotIn(views.DOCS_ACCESS, views.DOCS_ACCESS_CHOICES)

    @tag("coreplus_docs_unit_testing")
    def test_docs_index_html(self):
        self.assertRaises(
            views.DocsAccessSettingError,
            views.serve_docs,
            self.rf.request(),
            "index.html",
        )


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS="public")
class PublicAccessTest(DocsViewsTestBase):
    @tag("coreplus_docs_unit_testing")
    def test_docs_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertEqual(views.DOCS_ACCESS, "public")
        self.assertEqual(views.DOCS_DIRHTML, False)

    @tag("coreplus_docs_unit_testing")
    def test_docs_index_html(self):
        self.assertEqual(
            views.serve_docs(self.rf.request(), "index.html").status_code, 200
        )

    @tag("coreplus_docs_unit_testing")
    def test_docs_incorrect_path(self):
        self.assertRaises(Http404, views.serve_docs, self.rf.request(), "wrong.html")

    @tag("coreplus_docs_unit_testing")
    def test_docs_sub_directory_path(self):
        self.assertRaises(Http404, views.serve_docs, self.rf.request(), "sub_dir/")

    @tag("coreplus_docs_unit_testing")
    def test_docs_root_redirects(self):
        docs_url = reverse("docs_root")
        response = self.client.get(docs_url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, docs_url + "index.html")


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS="public", DOCS_DIRHTML=True)
class DIRHTMLTest(DocsViewsTestBase):
    @tag("coreplus_docs_unit_testing")
    def test_docs_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertEqual(views.DOCS_ACCESS, "public")
        self.assertEqual(views.DOCS_DIRHTML, True)

    @tag("coreplus_docs_unit_testing")
    def test_docs_sub_directory_path_with_trailing_slash(self):
        self.assertEqual(
            views.serve_docs(self.rf.request(), "sub_dir/").status_code, 200
        )

    @tag("coreplus_docs_unit_testing")
    def test_docs_sub_directory_path_without_trailing_slash(self):
        self.assertEqual(
            views.serve_docs(self.rf.request(), "sub_dir").status_code, 200
        )


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS="login_required")
class LoginAccessTest(DocsViewsTestBase):
    @tag("coreplus_docs_unit_testing")
    def test_docs_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertEqual(views.DOCS_ACCESS, "login_required")

    @tag("coreplus_docs_unit_testing")
    def test_docs_index_html(self):
        request = self.rf.request()
        request.user = self.user
        response = views.serve_docs(request, "index.html")
        self.assertEqual(response.status_code, 200)
