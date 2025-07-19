#!/usr/bin/env python3
"""
Utilities module.

This module provides utility functions for accessing nested data structures,
making HTTP requests, and memoization functionality.
"""

import requests
from typing import Mapping, Sequence, Any, Dict, Callable


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """
    Access nested map with key path.
    
    Args:
        nested_map: A nested map
        path: A sequence of key representing a path to the value
        
    Returns:
        The value at the given path
        
    Raises:
        KeyError: If the path is invalid
        
    Example:
        >>> access_nested_map({"a": {"b": 2}}, ("a", "b"))
        2
    """
    for key in path:
        nested_map = nested_map[key]
    return nested_map


def get_json(url: str) -> Dict:
    """
    Get JSON from remote URL.
    
    Args:
        url: The URL to fetch JSON from
        
    Returns:
        The JSON response as a dictionary
        
    Example:
        >>> get_json("http://example.com/api")
        {"data": "example"}
    """
    response = requests.get(url)
    return response.json()


def memoize(fn: Callable) -> Callable:
    """
    Memoization decorator.
    
    This decorator caches the result of a method call so that subsequent
    calls with the same arguments return the cached result instead of
    recomputing it.
    
    Args:
        fn: Function to memoize
        
    Returns:
        Memoized function as a property
        
    Example:
        class MyClass:
            @memoize
            def expensive_operation(self):
                return some_expensive_computation()
    """
    def wrapper(self):
        """Wrapper function for memoization."""
        attr_name = f"_{fn.__name__}"
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return property(wrapper)
