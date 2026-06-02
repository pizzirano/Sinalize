#!/usr/bin/env python
"""
Inspect rendered HTML of two pages to identify footer layout issues.
"""
import os
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client

client = Client()

def inspect_page(url, label, follow=False):
    print("=" * 80)
    print(f"PAGE: {label}")
    print("=" * 80)
    try:
        response = client.get(url, follow=follow)
        print(f"Status: {response.status_code}")
        
        if response.status_code in [301, 302, 303, 307, 308]:
            print(f"Redirect to: {response.url}")
        
        html = response.content.decode('utf-8')
        print(f"HTML length: {len(html)} chars")
        has_main = '<main id="main"' in html
        has_footer = '<footer' in html
        has_base_css = 'static/css/base.css' in html
        print(f"Has <main id='main'>: {has_main}")
        print(f"Has <footer>: {has_footer}")
        print(f"Has static/css/base.css: {has_base_css}")
        
        if len(html) > 100:
            # Extract body tag
            body_match = re.search(r'<body[^>]*>', html)
            if body_match:
                body_tag = body_match.group(0)
                print(f"\n<body> tag: {body_tag}")
            
            # Check for main
            main_match = re.search(r'<main[^>]*id="main"[^>]*>', html)
            if main_match:
                main_tag = main_match.group(0)
                print(f"\n<main> tag found: {main_tag}")
            
            # Check footer
            footer_match = re.search(r'<footer[^>]*>', html)
            if footer_match:
                footer_tag = footer_match.group(0)
                print(f"\n<footer> tag found: {footer_tag}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()

# Inspect both pages - first without following redirects
print("WITHOUT FOLLOWING REDIRECTS:")
print()
inspect_page('/catalog/home/', '/catalog/home/', follow=False)
inspect_page('/forms/minhas-submissoes/', '/forms/minhas-submissoes/', follow=False)

print("\n\nWITH FOLLOWING REDIRECTS:")
print()
inspect_page('/catalog/home/', '/catalog/home/', follow=True)
inspect_page('/forms/minhas-submissoes/', '/forms/minhas-submissoes/', follow=True)

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
