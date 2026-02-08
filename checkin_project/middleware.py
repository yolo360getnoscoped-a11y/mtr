"""
Custom middleware for adding cache headers and fixing content-type
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import os


class StaticFilesCacheMiddleware(MiddlewareMixin):
    """
    Middleware to add cache-control headers for static files
    """
    def process_response(self, request, response):
        # Check if this is a static file request
        if request.path.startswith(settings.STATIC_URL) or request.path.startswith('/static/'):
            # Add cache headers for static files
            response['Cache-Control'] = 'public, max-age=31536000, immutable'
            # Remove Expires header if present (use Cache-Control instead)
            if 'Expires' in response:
                del response['Expires']
        
        # Fix content-type for font files
        if request.path.endswith('.woff2'):
            response['Content-Type'] = 'font/woff2'
        elif request.path.endswith('.woff'):
            response['Content-Type'] = 'font/woff'
        elif request.path.endswith('.ttf'):
            response['Content-Type'] = 'font/ttf'
        elif request.path.endswith('.eot'):
            response['Content-Type'] = 'application/vnd.ms-fontobject'
        
        # Ensure UTF-8 charset for text files (but not for fonts or binary files)
        content_type = response.get('Content-Type', '')
        if content_type:
            # Remove charset from content-type if it's a font or binary file
            if 'font' in content_type or 'woff' in content_type or 'ttf' in content_type or 'eot' in content_type:
                # Font files should not have charset
                if 'charset' in content_type:
                    response['Content-Type'] = content_type.split(';')[0].strip()
            elif (content_type.startswith('text/') or 
                  'text/css' in content_type or
                  content_type.startswith('application/javascript') or
                  content_type.startswith('application/json')) and 'charset' not in content_type:
                # Text files, CSS, JS, and JSON should have charset=utf-8
                response['Content-Type'] = f"{content_type}; charset=utf-8"
        
        return response

