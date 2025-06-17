# Git Repository Setup Guide

This guide will walk you through the process of setting up a Git repository for your Cybersecurity KPI Dashboard project and pushing it to a remote repository (like GitHub or GitLab).

## Prerequisites

1. **Git Installation**: Make sure Git is installed on your computer.
   - To check, open a terminal/command prompt and type: `git --version`
   - If not installed, download from: https://git-scm.com/downloads

2. **GitHub/GitLab Account**: Create an account on GitHub (https://github.com/) or GitLab (https://gitlab.com/) if you don't have one already.

## Step 1: Initialize the Local Repository

You can use one of the provided scripts:

**Using the Batch Script (Windows):**
```
.\setup_git_repo.bat
```

**Using the PowerShell Script (Windows):**
```
.\Setup-GitRepo.ps1
```

**Or manually run the commands:**
```
git init
git add .
git commit -m "Initial commit of Cybersecurity KPI Dashboard"
```

## Step 2: Create a Remote Repository

1. **Go to GitHub/GitLab**: Login to your account
2. **Create a new repository**:
   - Click the "+" icon and select "New repository"
   - Name your repository (e.g., "cybersecurity-kpi-dashboard")
   - Add a description (optional)
   - Choose public or private
   - Do NOT initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

## Step 3: Link Local Repository to Remote

After creating the repository, you'll see instructions. Run these commands in your terminal:

```
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_URL` with the URL of your repository. For example:
```
git remote add origin https://github.com/yourusername/cybersecurity-kpi-dashboard.git
git push -u origin main
```

If you're using the main branch instead of master:
```
git push -u origin main
```

## Step 4: Verify the Push

Go to your GitHub/GitLab repository URL and refresh the page. You should see all your project files there.

## Common Issues and Solutions

1. **Authentication Failed**: You might need to authenticate with GitHub/GitLab.
   - For HTTPS: You'll be prompted for username and password
   - For SSH: Make sure your SSH keys are set up correctly

2. **Cannot Push to Repository**: If you get errors about the remote containing work you don't have locally:
   ```
   git pull --rebase origin main
   git push origin main
   ```

3. **Branch Name Issues**: If your local branch is called "master" instead of "main":
   ```
   git branch -M main
   git push -u origin main
   ```

## Next Steps After Pushing

1. Add collaborators to your repository if needed
2. Set up issues for tracking bugs and features
3. Consider setting up GitHub Actions or GitLab CI for automated testing

## Regular Git Workflow

After initial setup, your regular workflow will be:

```
git add .
git commit -m "Description of your changes"
git push
```

## Additional Resources

- GitHub Documentation: https://docs.github.com/
- GitLab Documentation: https://docs.gitlab.com/
- Git Documentation: https://git-scm.com/doc
