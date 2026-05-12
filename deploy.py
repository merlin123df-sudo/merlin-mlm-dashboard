#!/usr/bin/env python3
"""
Merlin MLM Dashboard - Automated Deployment to GitHub & Streamlit Cloud
Run this script to deploy your dashboard instantly!
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path

# Configuration
GITHUB_TOKEN = None  # User will provide this
GITHUB_USERNAME = None
REPO_NAME = "merlin-mlm-dashboard"
REPO_DESCRIPTION = "Merlin MLM Operations Dashboard with ML-powered Warehouse Prediction"

def print_step(step_num, message):
    """Print formatted step message"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {message}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def get_github_credentials():
    """Get GitHub credentials from user"""
    print("\n" + "="*60)
    print("GITHUB SETUP")
    print("="*60)
    
    print("\n📋 STEP 1: Get GitHub Token")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Set scopes: repo (all), gist, delete_repo")
    print("4. Copy the token")
    
    github_token = input("\n🔑 Paste your GitHub token: ").strip()
    github_username = input("👤 Enter your GitHub username: ").strip()
    
    return github_token, github_username

def create_github_repo(token, username):
    """Create GitHub repository via API"""
    print_step(1, "Creating GitHub Repository")
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": REPO_NAME,
        "description": REPO_DESCRIPTION,
        "public": True,
        "auto_init": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            repo_data = response.json()
            print_success(f"Repository created: {repo_data['html_url']}")
            return repo_data
        elif response.status_code == 422:
            print("⚠️  Repository already exists. Using existing...")
            # Get existing repo
            url = f"https://api.github.com/repos/{username}/{REPO_NAME}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        else:
            print_error(f"Failed to create repository: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def upload_files_to_github(token, username, repo_name):
    """Upload project files to GitHub"""
    print_step(2, "Uploading Files to GitHub")
    
    base_url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Files to upload
    files_to_upload = [
        "app.py",
        "ml_engine.py",
        "pipeline.py",
        "requirements.txt",
        "streamlit_app.py",
        "setup.py",
        "README.md",
        ".streamlit/config.toml",
        ".gitignore"
    ]
    
    uploaded = 0
    failed = 0
    
    for file_path in files_to_upload:
        full_path = Path("c:/Users/amjad/OneDrive/Documents/python") / file_path
        
        if not full_path.exists():
            print(f"⚠️  Skipping {file_path} (not found)")
            continue
        
        try:
            with open(full_path, "rb") as f:
                file_content = f.read()
            
            # Encode content
            encoded_content = base64.b64encode(file_content).decode()
            
            # Upload
            upload_url = f"{base_url}/{file_path}"
            data = {
                "message": f"Add {file_path}",
                "content": encoded_content,
                "branch": "main"
            }
            
            response = requests.put(upload_url, headers=headers, json=data)
            
            if response.status_code in [201, 200]:
                print_success(f"Uploaded: {file_path}")
                uploaded += 1
            else:
                print_error(f"Failed to upload {file_path}")
                failed += 1
                
        except Exception as e:
            print_error(f"Error uploading {file_path}: {e}")
            failed += 1
    
    print(f"\n✅ Files uploaded: {uploaded}/{len(files_to_upload)}")
    return uploaded > 0

def create_database_file(token, username, repo_name):
    """Upload database file to GitHub"""
    print_step(3, "Uploading Database")
    
    db_path = Path("c:/Users/amjad/OneDrive/Documents/python/processed_db/warehouse.db")
    
    if not db_path.exists():
        print_error("Database file not found")
        return False
    
    try:
        with open(db_path, "rb") as f:
            db_content = f.read()
        
        encoded_content = base64.b64encode(db_content).decode()
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        upload_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/processed_db/warehouse.db"
        data = {
            "message": "Add database",
            "content": encoded_content,
            "branch": "main"
        }
        
        response = requests.put(upload_url, headers=headers, json=data)
        
        if response.status_code in [201, 200]:
            print_success("Database uploaded")
            return True
        else:
            print_error(f"Failed to upload database: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error uploading database: {e}")
        return False

def show_streamlit_deployment_steps(username):
    """Show steps for Streamlit Cloud deployment"""
    print_step(4, "Deploy on Streamlit Cloud")
    
    repo_url = f"https://github.com/{username}/{REPO_NAME}"
    
    print(f"""
📱 Now deploy on Streamlit Cloud:

1. Go to: https://share.streamlit.io
2. Click "New App"
3. Select "GitHub"
4. Enter repository: {username}/{REPO_NAME}
5. Set branch: main
6. Set file path: app.py
7. Click "Deploy"

✨ Your dashboard will be live in 2-3 minutes!

📊 Dashboard URL: https://[auto-generated].streamlit.app
📂 Repository: {repo_url}

Share the Streamlit link with your founder! 🚀
    """)

def main():
    """Main deployment workflow"""
    print("""
╔════════════════════════════════════════════════════════╗
║   MERLIN MLM DASHBOARD - AUTOMATED DEPLOYMENT         ║
║   Deploy to GitHub & Streamlit Cloud in 5 minutes!    ║
╚════════════════════════════════════════════════════════╝
    """)
    
    # Get GitHub credentials
    print("\n⚠️  IMPORTANT: You need a GitHub account first!")
    print("Create one at: https://github.com/signup\n")
    
    try:
        github_token, github_username = get_github_credentials()
    except KeyboardInterrupt:
        print_error("Deployment cancelled")
        return
    
    if not github_token or not github_username:
        print_error("GitHub credentials required")
        return
    
    # Create repository
    repo = create_github_repo(github_token, github_username)
    if not repo:
        return
    
    # Upload files
    if not upload_files_to_github(github_token, github_username, REPO_NAME):
        print_error("Failed to upload files")
        return
    
    # Upload database
    create_database_file(github_token, github_username, REPO_NAME)
    
    # Show Streamlit steps
    show_streamlit_deployment_steps(github_username)
    
    print_success("GitHub setup complete! Now follow Streamlit Cloud steps above.")

if __name__ == "__main__":
    main()
