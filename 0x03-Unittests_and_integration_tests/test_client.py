#!/usr/bin/env python3
"""Unit and integration tests for client module."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value."""
        expected_payload = {"name": org_name}
        mock_get_json.return_value = expected_payload
        
        client = GithubOrgClient(org_name)
        result = client.org
        
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url property."""
        expected_url = "https://api.github.com/orgs/test-org/repos"
        payload = {"repos_url": expected_url}
        
        with patch.object(GithubOrgClient, 'org',
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("test-org")
            
            result = client._public_repos_url
            self.assertEqual(result, expected_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos method."""
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = test_payload
        
        with patch.object(GithubOrgClient, '_public_repos_url',
                          new_callable=PropertyMock) as mock_repos_url:
            test_url = "https://api.github.com/orgs/test-org/repos"
            mock_repos_url.return_value = test_url
            
            client = GithubOrgClient("test-org")
            result = client.public_repos()
            
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license method."""
        client = GithubOrgClient("test-org")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient class."""

    @classmethod
    def setUpClass(cls):
        """Set up class for integration tests."""
        def get_side_effect(url):
            """Side effect function for mocking requests.get."""
            from unittest.mock import Mock
            mock_response = Mock()
            org_url = f"https://api.github.com/orgs/{cls.org_payload['login']}"
            if url == org_url:
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response

        cls.get_patcher = patch('requests.get', side_effect=get_side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class after integration tests."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos method."""
        client = GithubOrgClient(self.org_payload['login'])
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test for public_repos method with license filtering."""
        client = GithubOrgClient(self.org_payload['login'])
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
