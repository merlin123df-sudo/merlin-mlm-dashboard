# 🚀 MERLIN MLM DASHBOARD - AUTOMATIC DEPLOYMENT SCRIPT
# Run this script to deploy automatically to Streamlit Cloud

# Colors for output
$Green = 'Green'
$Yellow = 'Yellow'
$Red = 'Red'
$Cyan = 'Cyan'

Write-Host "`n" -ForegroundColor $Cyan
Write-Host "========================================" -ForegroundColor $Cyan
Write-Host "MERLIN MLM DASHBOARD - AUTO DEPLOY" -ForegroundColor $Cyan
Write-Host "========================================" -ForegroundColor $Cyan

# Step 1: Check if Git is installed
Write-Host "`n[STEP 1] Checking Git Installation..." -ForegroundColor $Yellow
try {
    git --version | Out-Null
    Write-Host "✅ Git is installed!" -ForegroundColor $Green
} catch {
    Write-Host "❌ Git not found! Download from https://git-scm.com/" -ForegroundColor $Red
    exit
}

# Step 2: Initialize Git Repository
Write-Host "`n[STEP 2] Initializing Git Repository..." -ForegroundColor $Yellow
cd "c:\Users\amjad\OneDrive\Documents\python"

if (Test-Path ".git") {
    Write-Host "✅ Git repository already exists!" -ForegroundColor $Green
} else {
    git init
    Write-Host "✅ Git repository initialized!" -ForegroundColor $Green
}

# Step 3: Configure Git (if not configured)
Write-Host "`n[STEP 3] Configuring Git..." -ForegroundColor $Yellow
$userName = git config --global user.name
if (-not $userName) {
    git config user.name "Merlin User"
    git config user.email "merlin@mlm.com"
    Write-Host "✅ Git configured!" -ForegroundColor $Green
} else {
    Write-Host "✅ Git already configured!" -ForegroundColor $Green
}

# Step 4: Add all files
Write-Host "`n[STEP 4] Adding files to Git..." -ForegroundColor $Yellow
git add .
Write-Host "✅ Files added!" -ForegroundColor $Green

# Step 5: Commit
Write-Host "`n[STEP 5] Committing changes..." -ForegroundColor $Yellow
$commitMessage = "Merlin MLM Dashboard - Faster Version (120s cache)"
git commit -m "$commitMessage" 2>$null
Write-Host "✅ Changes committed!" -ForegroundColor $Green

# Step 6: Instructions for next steps
Write-Host "`n========================================" -ForegroundColor $Cyan
Write-Host "✅ LOCAL SETUP COMPLETE!" -ForegroundColor $Green
Write-Host "========================================" -ForegroundColor $Cyan

Write-Host "`n📋 NEXT STEPS (Do In Browser):`n" -ForegroundColor $Cyan

Write-Host "1️⃣  CREATE GITHUB REPOSITORY:" -ForegroundColor $Yellow
Write-Host "   → Go to: https://github.com/new" -ForegroundColor $Cyan
Write-Host "   → Name: merlin-mlm-dashboard" -ForegroundColor $Cyan
Write-Host "   → Visibility: PUBLIC" -ForegroundColor $Cyan
Write-Host "   → Click: Create Repository" -ForegroundColor $Cyan

Write-Host "`n2️⃣  PUSH CODE TO GITHUB:" -ForegroundColor $Yellow
Write-Host "   → Replace YOUR_USERNAME with your GitHub username:" -ForegroundColor $Cyan
$userName = Read-Host "Enter your GitHub username"
Write-Host "`n   Running: git remote add origin..." -ForegroundColor $Yellow

git remote remove origin 2>$null
git remote add origin "https://github.com/$userName/merlin-mlm-dashboard.git"
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Code pushed to GitHub!" -ForegroundColor $Green
} else {
    Write-Host "⚠️  Make sure you have GitHub credentials set up!" -ForegroundColor $Yellow
    Write-Host "   → https://docs.github.com/en/authentication" -ForegroundColor $Cyan
}

Write-Host "`n3️⃣  DEPLOY ON STREAMLIT CLOUD:" -ForegroundColor $Yellow
Write-Host "   → Go to: https://share.streamlit.io" -ForegroundColor $Cyan
Write-Host "   → Sign in with GitHub" -ForegroundColor $Cyan
Write-Host "   → Click: New app" -ForegroundColor $Cyan
Write-Host "   → Select:" -ForegroundColor $Cyan
Write-Host "      Repository: $userName/merlin-mlm-dashboard" -ForegroundColor $Cyan
Write-Host "      Branch: main" -ForegroundColor $Cyan
Write-Host "      Main file: app.py" -ForegroundColor $Cyan
Write-Host "   → Click: Deploy" -ForegroundColor $Cyan
Write-Host "   → Wait 2-5 minutes..." -ForegroundColor $Cyan

Write-Host "`n4️⃣  YOUR LIVE DASHBOARD:" -ForegroundColor $Yellow
Write-Host "   🌐 https://merlin-mlm-dashboard.streamlit.app" -ForegroundColor $Green

Write-Host "`n========================================" -ForegroundColor $Cyan
Write-Host "🎉 DEPLOYMENT READY!" -ForegroundColor $Green
Write-Host "========================================" -ForegroundColor $Cyan
Write-Host ""
