#!/usr/bin/env python
"""
Inspect rendered HTML with proper authentication.
"""
import os
import django
import re
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client

User = get_user_model()
client = Client()

# Check for existing test user
users = User.objects.all()
print(f"Existing users in database: {users.count()}")
for user in users[:5]:
    print(f"  - {user.username} (is_staff={user.is_staff})")

# Try to create or get a test user
test_user = None
try:
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"\nCreated test user: testuser")
    else:
        # Reset password for existing user
        test_user.set_password('testpass123')
        test_user.save()
        print(f"\nUsing existing test user: testuser")
except Exception as e:
    print(f"Error creating test user: {e}")
    test_user = None

if test_user:
    # Try to login
    login_success = client.login(username='testuser', password='testpass123')
    print(f"Login success: {login_success}")
    
    if login_success:
        # Now try to access the forms page
        print("\n" + "=" * 80)
        print("PAGE: /forms/minhas-submissoes/ (AUTHENTICATED)")
        print("=" * 80)
        response = client.get('/forms/minhas-submissoes/')
        print(f"Status: {response.status_code}")
        
        html = response.content.decode('utf-8')
        print(f"HTML length: {len(html)} chars")
        
        if len(html) > 100:
            has_main = '<main id="main"' in html
            has_footer = '<footer' in html
            print(f"Has <main id='main'>: {has_main}")
            print(f"Has <footer>: {has_footer}")
            
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
            
            # Look for main content wrapper
            print("\n\nSearching for content structure...")
            # Get the snippet between main and footer
            main_pos = html.find('<main')
            footer_pos = html.find('<footer')
            if main_pos != -1 and footer_pos != -1:
                main_content = html[main_pos:footer_pos+200]
                print("Structure between <main> and <footer>:")
                print(main_content[:800])
else:
    print("Could not create or login test user")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
