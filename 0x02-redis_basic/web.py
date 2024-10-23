#!/usr/bin/env python3
"""
Web cache and tracker module
"""
import redis
import requests
from typing import Callable
from functools import wraps
from datetime import timedelta


def cache_with_expiry(expiry_time: int = 10) -> Callable:
    """
    Decorator to cache the result of a function with expiration time
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            # Create Redis client
            redis_client = redis.Redis()
            
            # Create keys for count and content
            count_key = f'count:{url}'
            content_key = f'content:{url}'
            
            # Increment the access count
            redis_client.incr(count_key)
            
            # Try to get cached content
            cached_content = redis_client.get(content_key)
            if cached_content:
                return cached_content.decode('utf-8')
            
            # If no cached content, make the request
            content = func(url)
            
            # Cache the new content with expiration
            redis_client.setex(content_key, 
                             timedelta(seconds=expiry_time), 
                             content)
            
            return content
        return wrapper
    return decorator


@cache_with_expiry()
def get_page(url: str) -> str:
    """
    Obtain the HTML content of a URL
    
    Args:
        url: The URL to fetch
        
    Returns:
        str: The HTML content of the page
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Example usage and testing
    url = "http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.google.com"
    
    # Get the page multiple times to test caching
    page_content = get_page(url)
    print(f"Length of content: {len(page_content)}")
    
    # Get it again (should be cached)
    page_content = get_page(url)
    print(f"Length of content: {len(page_content)}")
