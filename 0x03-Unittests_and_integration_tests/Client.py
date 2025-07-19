#!/usr/bin/env python3
"""GitHub organization client module."""

from typing import List, Dict
from utils import get_json, access_nested_map, memoize


class GithubOrgClient:
    """GitHub organization client."""
    
    ORG_URL = "https://api.github.com/orgs/{org}"
    
    def __init__(self, org_name: str) -> None:
        """Initialize GitHub organization client.
        
        Args:
            org_name: Name of the organization
        """
        self._org_name = org_name
    
    @memoize
    def org(self) -> Dict:
        """Get organization information.
        
        Returns:
            Organization information as dictionary
        """
        return get_json(self.ORG_URL.format(org=self._org_name))
    
    @property
    def _public_repos_url(self) -> str:
        """Get public repositories URL.
        
        Returns:
            URL for public repositories
        """
        return self.org["repos_url"]
    
    def public_repos(self, license: str = None) -> List[str]:
        """Get public repositories.
        
        Args:
            license: License type to filter by (optional)
            
        Returns:
            List of repository names
        """
        repos = get_json(self._public_repos_url)
        
        if license is not None:
            return [
                repo["name"] for repo in repos
                if self.has_license(repo, license)
            ]
        
        return [repo["name"] for repo in repos]
    
    @staticmethod
    def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
        """Check if repository has specific license.
        
        Args:
            repo: Repository information
            license_key: License key to check for
            
        Returns:
            True if repository has the license, False otherwise
        """
        assert license_key is not None, "license_key cannot be None"
        assert "license" in repo, "repo must have a license key"
        assert "key" in repo["license"], "license must have a key"
        
        return repo["license"]["key"] == license_key
