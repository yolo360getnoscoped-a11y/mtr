"""
Script to download Font Awesome files for local use
This will download Font Awesome 6.4.0 CSS and fonts to static directory
"""
import os
import urllib.request
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
CSS_DIR = STATIC_DIR / 'css' / 'fontawesome'
FONTS_DIR = STATIC_DIR / 'webfonts'

# Create directories
CSS_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Font Awesome 6.4.0 files to download
FILES = {
    'css': {
        'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
        'path': CSS_DIR / 'all.min.css'
    },
    'fonts': [
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2',
            'path': FONTS_DIR / 'fa-brands-400.woff2'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2',
            'path': FONTS_DIR / 'fa-regular-400.woff2'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2',
            'path': FONTS_DIR / 'fa-solid-900.woff2'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-v4compatibility.woff2',
            'path': FONTS_DIR / 'fa-v4compatibility.woff2'
        },
    ]
}

def download_file(url, filepath):
    """Download a file from URL to filepath"""
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ Saved to {filepath}")
        return True
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def main():
    print("=" * 60)
    print("Font Awesome 6.4.0 Local Installation")
    print("=" * 60)
    
    # Download CSS
    print("\n[1/2] Downloading CSS file...")
    css_file = FILES['css']
    if download_file(css_file['url'], css_file['path']):
        # Update CSS to use local fonts
        print("\nUpdating CSS to use local fonts...")
        with open(css_file['path'], 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Replace CDN font paths with local paths
        css_content = css_content.replace(
            '../webfonts/',
            '/static/webfonts/'
        )
        
        with open(css_file['path'], 'w', encoding='utf-8') as f:
            f.write(css_content)
        print("✓ CSS updated to use local fonts")
    
    # Download fonts
    print("\n[2/2] Downloading font files...")
    success_count = 0
    for font in FILES['fonts']:
        if download_file(font['url'], font['path']):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Download complete! ({success_count}/{len(FILES['fonts'])} fonts downloaded)")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update templates to use: {% static 'css/fontawesome/all.min.css' %}")
    print("2. Restart Django server")
    print("=" * 60)

if __name__ == '__main__':
    main()

