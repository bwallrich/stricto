"test module acls"

import unittest
from stricto import AccessControlList, RegexAccessControlItem


class TestACLS(unittest.TestCase):
    """class of test AccessControlList"""

    def __init__(self, *args, **kwargs):
        "init test AccessControlList"
        super().__init__(*args, **kwargs)

    def test_authorize_is_a_whitelist_and_default_is_false(self):
        """*test if RegexAccessControlItem is a whitelist et result equal true so accept a domain"""

        l = AccessControlList(
            [
                RegexAccessControlItem("toto.titi@mail.com", True),
                RegexAccessControlItem("fifi.com", True),
                RegexAccessControlItem("fofo.org", True),
            ],
            default=False,
        )

        self.assertTrue(l.accept("fifi.com"))

    def test_authorize_is_a_not_whitelist_and_default_true(self):
        """list AccessControlList that return False"""
        l = AccessControlList(
            [
                RegexAccessControlItem("example.fr", False),
                RegexAccessControlItem("coctiti.com", False),
                RegexAccessControlItem("fifi.org", False),
            ],
            default=True,
        )

        self.assertFalse(l.accept("fifi.org"))

    def test_authorize_is_whitelist_and_is_not_whitelist_not_accept(self):
        """list AccessControlList who accept if acls is not whitelist and not accept"""
        l = AccessControlList(
            [
                RegexAccessControlItem("tootio.titi.fr", True),
                RegexAccessControlItem("caprice@gmail.org", False),
                RegexAccessControlItem("titi.fr", False),
                RegexAccessControlItem(r".*\.captivee.com", True),
                RegexAccessControlItem("captivif.fr", True),
            ],
            default=False,
        )
        self.assertFalse(l.accept("titi.fr"))

    def test_authorize_is_whitelist_ant_is_not_whitlist_is_accept(self):
        """list acls who accept if donmain is accept and not whitelist"""

        l = AccessControlList(
            [
                RegexAccessControlItem("tootio.titi.fr", True),
                RegexAccessControlItem("caprice@gmail.org", False),
                RegexAccessControlItem("titifine.fr", True),
                RegexAccessControlItem(r".*\.captivee.com", True),
                RegexAccessControlItem("titifine.fr", True),
            ],
            default=False,
        )
        self.assertTrue(l.accept("titifine.fr"))

    def test_not_math_and_is_whitelist(self):
        """not math"""

        l = AccessControlList(
            [
                RegexAccessControlItem("coctiti.com", False),
                RegexAccessControlItem("foutooo.org", True),
                RegexAccessControlItem("pipooo.org", False),
                RegexAccessControlItem("tooo.org", True),
            ],
            default=True,
        )
        self.assertTrue(l.accept("foutooou.org"))

    def test_math_and_is_not_whitelist(self):
        """match and is not whitelist"""

        l = AccessControlList(
            [
                RegexAccessControlItem("toiti.fr", True),
                RegexAccessControlItem("gogo.com", False),
                RegexAccessControlItem("nanotooi.fr", True),
                RegexAccessControlItem("gogo.com", True),
            ],
            default=True,
        )
        self.assertFalse(l.accept("gogo.com"))

    def test_not_match_and_is_not_whitelist(self):
        """notch and not whitelist"""

        l = AccessControlList(
            [
                RegexAccessControlItem(r".*toto\.fr", True),
                RegexAccessControlItem(r".*fr", False),
                RegexAccessControlItem(r".*gogo\.com", True),
            ],
            default=False,
        )
        self.assertFalse(l.accept("gogoco.com"))
        self.assertTrue(l.accept("gogo.com"))
        self.assertTrue(l.accept("toto.fr"))
        self.assertTrue(l.accept("titi.toto.fr"))
        self.assertFalse(l.accept("tata.fr"))

    def test_acl_with_values(self):
        """notch and not whitelist"""

        l = AccessControlList(
            [
                RegexAccessControlItem(r".*toto\.fr", "JAVA"),
                RegexAccessControlItem(r".*\.fr", "PYTHON"),
                RegexAccessControlItem(r".*gogo\.com", "RUBY"),
                RegexAccessControlItem(r".*.com", "C"),
            ],
            default="PERL",
        )
        self.assertEqual(l.accept("gogoco.com"), "C")
        self.assertEqual(l.accept("gogo.com"), "RUBY")
        self.assertEqual(l.accept("toto.fr"), "JAVA")
        self.assertEqual(l.accept("titi.toto.fr"), "JAVA")
        self.assertEqual(l.accept("tata.fr"), "PYTHON")
        self.assertEqual(l.accept("tata.eu"), "PERL")
