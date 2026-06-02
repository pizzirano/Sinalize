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

def extract_between(html, start_tag, end_tag, limit=500):
    """Extract content between two tags."""
    start_idx = html.find(start_tag)
    if start_idx == -1:
        return None
    start_idx += len(start_tag)
    end_idx = html.find(end_tag, start_idx)
    if end_idx == -1:
        end_idx = len(html)
    return html[start_idx:min(end_idx, start_idx + limit)]

def inspect_page(url, label):
    print("=" * 80)
    print(f"PAGE: {label}")
    print("=" * 80)
    try:
        response = client.get(url)
        print(f"Status: {response.status_code}")
        
        html = response.content.decode('utf-8')
        print(f"HTML length: {len(html)} chars")
        has_main = '<main id="main"' in html
        has_footer = '<footer' in html
        has_base_css = 'static/css/base.css' in html
        print(f"Contains <main id=\"main\">: {has_main}")
        print(f"Contains <footer: {has_footer}")
        print(f"Contains static/css/base.css: {has_base_css}")
        
        # Extract body tag
        body_match = re.search(r'<body[^>]*>', html)
        if body_match:
            body_tag = body_match.group(0)
            print(f"\n<body> tag: {body_tag}")
        
        # Extract body content (first 1000 chars after <body>)
        body_start = html.find('<body')
        if body_start != -1:
            body_content_start = html.find('>', body_start) + 1
            body_children_snippet = html[body_content_start:body_content_start + 1500]
            
            # Find all direct children tags
            print(f"\nFirst elements after <body>:")
            matches = re.findall(r'<(\w+)[^>]*>', body_children_snippet)
            seen = set()
            for tag in matches[:10]:  # Show first 10 unique tags
                if tag not in seen:
                    print(f"  - <{tag}>")
                    seen.add(tag)
        
        # Check if main exists and what's around it
        main_match = re.search(r'<main[^>]*id="main"[^>]*>', html)
        if main_match:
            main_tag = main_match.group(0)
            print(f"\n<main> tag found:")
            print(f"  {main_tag}")
        else:
            print(f"\n<main id='main'> NOT FOUND ⚠️")
        
        # Check footer
        footer_match = re.search(r'<footer[^>]*>', html)
        if footer_match:
            footer_tag = footer_match.group(0)
            print(f"\n<footer> tag found:")
            print(f"  {footer_tag}")
        else:
            print(f"\n<footer> NOT FOUND ⚠️")
        
        # Look for any divs or sections wrapping the content with problematic styles
        print(f"\nSearching for display/position/height styles in tags...")
        problem_tags = re.findall(r'<[^>]*(display|position|height|overflow)[^>]*>', html)
        if problem_tags:
            print(f"Found {len(problem_tags)} tags with display/position/height/overflow:")
            for tag in problem_tags[:5]:
                print(f"  {tag}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()

# Inspect both pages
inspect_page('/catalog/home/', '/catalog/home/')
inspect_page('/forms/minhas-submissoes/', '/forms/minhas-submissoes/')

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
