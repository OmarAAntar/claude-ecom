"""Tests for scripts/fetch_page.py SSRF protection.

Run with: python -m unittest tests/test_fetch_page.py
"""

from __future__ import annotations

import os
import socket
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.fetch_page import validate_url  # noqa: E402


def _mock_infos(*ip_strs: str) -> list:
    """Build a fake getaddrinfo return value for the given IPs."""
    out = []
    for ip in ip_strs:
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        out.append((family, socket.SOCK_STREAM, 6, "", (ip, 0)))
    return out


class TestSSRFBlocksKnownBadIPs(unittest.TestCase):
    """IP literals must be rejected without needing DNS."""

    def assertBlocked(self, url: str) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_url(url)
        # The error message should explain the block reason for debuggability.
        self.assertTrue(str(ctx.exception), "ValueError must carry a message")

    def test_127_0_0_1(self):
        self.assertBlocked("http://127.0.0.1/")

    def test_127_0_0_1_alt_loopback(self):
        self.assertBlocked("http://127.255.255.254/")

    def test_10_x(self):
        self.assertBlocked("http://10.0.0.1/")

    def test_172_17_docker_default(self):
        # The pre-fix code used "172.16." string prefix and missed this.
        self.assertBlocked("http://172.17.0.1/")

    def test_172_31_docker_high(self):
        self.assertBlocked("http://172.31.255.255/")

    def test_192_168(self):
        self.assertBlocked("http://192.168.1.1/")

    def test_169_254_aws_metadata(self):
        # AWS / cloud instance metadata endpoint.
        self.assertBlocked("http://169.254.169.254/latest/meta-data/")

    def test_100_64_cgnat(self):
        self.assertBlocked("http://100.64.1.1/")

    def test_0_0_0_0(self):
        self.assertBlocked("http://0.0.0.0/")

    def test_multicast(self):
        self.assertBlocked("http://224.0.0.1/")

    def test_ipv6_loopback(self):
        self.assertBlocked("http://[::1]/")

    def test_ipv6_link_local(self):
        self.assertBlocked("http://[fe80::1]/")

    def test_ipv6_unique_local(self):
        # fc00::/7 — IPv6 ULA, equivalent to RFC1918.
        self.assertBlocked("http://[fc00::1]/")


class TestSSRFBlocksLocalhostHostname(unittest.TestCase):
    def test_localhost(self):
        with self.assertRaises(ValueError):
            validate_url("http://localhost/")

    def test_localhost_https(self):
        with self.assertRaises(ValueError):
            validate_url("https://localhost/")


class TestSSRFAllowsPublicViaMockedDNS(unittest.TestCase):
    """Public-domain case (per task spec) uses mocked DNS so the test is hermetic."""

    def test_public_domain_allowed(self):
        # example.com's current public IP, mocked
        infos = _mock_infos("93.184.216.34")
        with patch("scripts.fetch_page.socket.getaddrinfo", return_value=infos):
            self.assertEqual(
                validate_url("https://example.com"),
                "https://example.com",
            )

    def test_dns_rebinding_to_private_blocked(self):
        infos = _mock_infos("10.0.0.5")
        with patch("scripts.fetch_page.socket.getaddrinfo", return_value=infos):
            with self.assertRaises(ValueError) as ctx:
                validate_url("https://attacker.example.com")
            self.assertIn("blocked", str(ctx.exception).lower())

    def test_dns_rebinding_to_aws_metadata_blocked(self):
        infos = _mock_infos("169.254.169.254")
        with patch("scripts.fetch_page.socket.getaddrinfo", return_value=infos):
            with self.assertRaises(ValueError):
                validate_url("https://innocent-looking.example.com")

    def test_mixed_public_and_private_blocked(self):
        # If ANY resolved IP is private, the whole hostname is rejected.
        infos = _mock_infos("93.184.216.34", "10.0.0.5")
        with patch("scripts.fetch_page.socket.getaddrinfo", return_value=infos):
            with self.assertRaises(ValueError):
                validate_url("https://mixed.example.com")

    def test_ipv6_rebinding_blocked(self):
        infos = _mock_infos("fc00::1")
        with patch("scripts.fetch_page.socket.getaddrinfo", return_value=infos):
            with self.assertRaises(ValueError):
                validate_url("https://ipv6attacker.example.com")

    def test_dns_failure_raises(self):
        with patch(
            "scripts.fetch_page.socket.getaddrinfo",
            side_effect=socket.gaierror("simulated NXDOMAIN"),
        ):
            with self.assertRaises(ValueError):
                validate_url("https://does-not-exist.example.invalid")


class TestSchemeAndShape(unittest.TestCase):
    def test_unsupported_scheme(self):
        with self.assertRaises(ValueError):
            validate_url("ftp://example.com/")

    def test_empty_url(self):
        with self.assertRaises(ValueError):
            validate_url("")

    def test_no_hostname(self):
        with self.assertRaises(ValueError):
            validate_url("https:///")

    def test_scheme_prefixed_when_missing(self):
        infos = _mock_infos("93.184.216.34")
        with patch("scripts.fetch_page.socket.getaddrinfo", return_value=infos):
            self.assertTrue(validate_url("example.com").startswith("https://"))


if __name__ == "__main__":
    unittest.main()
