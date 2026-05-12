#!/usr/bin/env python3
import os
import sys
import json
import base64
import requests
import time
from pathlib import Path

# Configuration
token = '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'
username = 'merlin123df-sudo'
repo_name = 'merlin-mlm-dashboard'

os.chdir('c:\\Users\\amjad\\OneDrive\\Documents\\python')

print('🔄 Starting automated deployment...')
print(f'✅ Token: {token[:10]}...')
print(f'✅ Username: {username}')
print(f'✅ Repository: {repo_name}')
print('')

# Setup headers
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
}

# 1. Check if repo exists
print('📦 Checking repository status...')
check_url = f'https://api.github.com/repos/{username}/{repo_name}'
check_response = requests.get(check_url, headers=headers)

if check_response.status_code == 200:
    print(f'✅ Repository already exists: {repo_name}')
elif check_response.status_code == 404:
    # Repository doesn't exist, create it
    print(f'📝 Repository not found, creating...')
    repo_data = {
        'name': repo_name,
        'description': 'Merlin MLM Operations Dashboard with ML-powered Warehouse Prediction',
        'private': False,
        'auto_init': True
    }
    
    response = requests.post('https://api.github.com/user/repos', 
                           json=repo_data, headers=headers)
    if response.status_code == 201:
        print(f'✅ Repository created successfully!')
    elif response.status_code == 422:
        print(f'✅ Repository already exists')
    else:
        print(f'❌ Error creating repository: {response.status_code}')
        print(response.text)
        sys.exit(1)
else:
    print(f'❌ Error checking repository: {check_response.status_code}')
    print(f'   {check_response.text}')
    sys.exit(1)

time.sleep(2)

# 2. Upload files
files_to_upload = [
    'app.py',
    'ml_engine.py', 
    'pipeline.py',
    'requirements.txt',
    'streamlit_app.py',
    'setup.py',
    'README.md',
]

print('')
print('📤 Uploading files to GitHub...')

for file_name in files_to_upload:
    file_path = Path(file_name)
    if file_path.exists():
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            encoded_content = base64.b64encode(content).decode('utf-8')
            
            upload_url = f'https://api.github.com/repos/{username}/{repo_name}/contents/{file_name}'
            
            upload_data = {
                'message': f'Add {file_name}',
                'content': encoded_content,
                'branch': 'main'
            }
            
            response = requests.put(upload_url, json=upload_data, headers=headers)
            if response.status_code in [201, 200]:
                print(f'✅ {file_name}')
            else:
                print(f'⚠️  {file_name}: {response.status_code}')
            time.sleep(0.5)
        except Exception as e:
            print(f'❌ {file_name}: {str(e)}')
    else:
        print(f'⚠️  {file_name} not found')

# 3. Create .streamlit directory and upload config
print('')
print('⚙️  Uploading configuration...')
config_path = Path('.streamlit/config.toml')
if config_path.exists():
    try:
        with open(config_path, 'rb') as f:
            content = f.read()
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        upload_url = f'https://api.github.com/repos/{username}/{repo_name}/contents/.streamlit/config.toml'
        upload_data = {
            'message': 'Add Streamlit configuration',
            'content': encoded_content,
            'branch': 'main'
        }
        response = requests.put(upload_url, json=upload_data, headers=headers)
        if response.status_code in [201, 200]:
            print('✅ .streamlit/config.toml')
    except Exception as e:
        print(f'❌ config.toml: {str(e)}')

# 4. Upload database
print('')
print('🗄️  Uploading database...')
db_path = Path('processed_db/warehouse.db')
if db_path.exists():
    try:
        with open(db_path, 'rb') as f:
            content = f.read()
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        upload_url = f'https://api.github.com/repos/{username}/{repo_name}/contents/processed_db/warehouse.db'
        upload_data = {
            'message': 'Add warehouse database',
            'content': encoded_content,
            'branch': 'main'
        }
        response = requests.put(upload_url, json=upload_data, headers=headers)
        if response.status_code in [201, 200]:
            print('✅ processed_db/warehouse.db')
    except Exception as e:
        print(f'❌ database: {str(e)}')

print('')
print('='*60)
print('🎉 DEPLOYMENT COMPLETE!')
print('='*60)
print('')
print('📍 Your GitHub Repository:')
print(f'🔗 https://github.com/{username}/{repo_name}')
print('')
print('⏭️  NEXT STEP: Deploy to Streamlit Cloud')
print('')
print('1. Go to: https://share.streamlit.io')
print('2. Click "New App"')
print('3. Connect GitHub account (if not already connected)')
print('4. Fill in:')
print(f'   • Repository: {username}/{repo_name}')
print('   • Branch: main')
print('   • File path: app.py')
print('5. Click "Deploy"')
print('')
print('⏳ Streamlit will build and deploy in 2-3 minutes')
print('')
print('✅ You will get a live URL like:')
print('   https://merlin-mlm-dashboard-xyz.streamlit.app')
print('')
print('🎯 Share this URL with your founder!')
print('='*60)
