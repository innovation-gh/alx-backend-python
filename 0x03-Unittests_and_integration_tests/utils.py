#!/usr/bin/env python3
"""Utilities module."""

import requests
from typing import Mapping, Sequence, Any, Dict, Callable


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access nested map with key path.
    
    Args:
        nested_map: A nested map
        path: A sequence of key representing a path to the value
        
    Returns:
        The value at the given path
        
    Raises:
        KeyError: If the path is invalid
    """
    for key in path:
        nested_map = nested_map[key]
    return nested_map


def get_json(url: str) -> Dict:
    """Get JSON from remote URL.
    
    Args:
        url: The URL to fetch JSON from
        
    Returns:
        The JSON response as a dictionary
    """
    response = requests.get(url)
    return response.json()


def memoize(fn: Callable) -> Callable:
    """Memoization decorator.
    
    Args:
        fn: Function to memoize
        
    Returns:
        Memoized function
    """
    def wrapper(self):
        attr_name = f"_{fn.__name__}"
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return property(wrapper)
