#!/usr/bin/env python3
"""
GitHub organization client module.
This module provides a client for interacting with GitHub's organization API,
allowing users to retrieve organization information and repository data.
"""
from typing import List, Dict
from utils import get_json, memoize


class GithubOrgClient:
    """
    GitHub organization client.
    
    This class provides methods to interact with GitHub's organization API
    to retrieve organization information and repository data.
    """
    
    ORG_URL = "https://api.github.com/orgs/{org}"
    
    def __init__(self, org_name: str) -> None:
        """
        Initialize GitHub organization client.
        
        Args:
            org_name: Name of the organization
        """
        self._org_name = org_name
    
    @memoize
    def org(self) -> Dict:
        """
        Get organization information.
        
        This method retrieves organization information from GitHub's API.
        The result is memoized to avoid repeated API calls.
        
        Returns:
            Organization information as dictionary
        """
        return get_json(self.ORG_URL.format(org=self._org_name))
    
    @property
    def _public_repos_url(self) -> str:
        """
        Get public repositories URL.
        
        Returns:
            URL for public repositories from the organization data
        """
        return self.org["repos_url"]
    
    def public_repos(self, license: str = None) -> List[str]:
        """
        Get public repositories.
        
        Retrieves a list of public repository names for the organization.
        Optionally filters repositories by license type.
        
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
        """
        Check if repository has specific license.
        
        Args:
            repo: Repository information dictionary
            license_key: License key to check for
            
        Returns:
            True if repository has the license, False otherwise
        """
        if license_key is None:
            return False
        
        if "license" not in repo or repo["license"] is None:
            return False
        
        if "key" not in repo["license"]:
            return False
        
        return repo["license"]["key"] == license_key
