"""Centralized API client to avoid code duplication across all pages."""

import streamlit as st
import httpx
import os

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

def make_api_request(method: str, endpoint: str, data=None):
    """Make a synchronous API request.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path
        data: Request data (for POST/PUT) or query params (for GET)

    Returns:
        dict: JSON response or None if failed
    """
    url = f"{API_BASE_URL}{endpoint}"
    try:
        with httpx.Client(timeout=30.0) as client:
            if method.upper() == "GET":
                response = client.get(url, params=data)
            elif method.upper() == "POST":
                response = client.post(url, json=data)
            elif method.upper() == "PUT":
                response = client.put(url, json=data)
            elif method.upper() == "DELETE":
                response = client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            # Handle 204 No Content (e.g., DELETE requests)
            if response.status_code == 204:
                return True
            return response.json()
    except httpx.HTTPStatusError as e:
        st.error(f"API request failed: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        st.error(f"API connection error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"API error: {str(e)}")
        return None