#!/bin/bash

# Initialize Git and push to GitHub
# Usage: ./init_git.sh <github_repo_url>

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

if [ "$#" -ne 1 ]; then
    echo -e "${RED}Error: Please provide your GitHub repository URL.${NC}"
    echo "Usage: ./init_git.sh <github_repo_url>"
    echo "Example: ./init_git.sh https://github.com/username/email-marketing-platform.git"
    exit 1
fi

GITHUB_REPO=$1

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: Git is not installed. Please install git first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting Git initialization process...${NC}"

# Backup the database first
echo -e "${YELLOW}Creating database backup...${NC}"
python backup_data.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Database backup failed. Please check errors and try again.${NC}"
    exit 1
fi

# Initialize git if .git doesn't exist
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to initialize Git repository.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Git repository already initialized.${NC}"
fi

# Set user information (prompting user)
echo -e "${YELLOW}Please enter your Git user information:${NC}"
read -p "Enter your name: " GIT_NAME
read -p "Enter your email: " GIT_EMAIL

git config user.name "$GIT_NAME"
git config user.email "$GIT_EMAIL"

# Add files to git
echo -e "${YELLOW}Adding files to Git repository...${NC}"
git add .
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to add files to Git repository.${NC}"
    exit 1
fi

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git commit -m "Initial commit of Email Marketing Platform"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to commit changes.${NC}"
    exit 1
fi

# Add remote repository
echo -e "${YELLOW}Adding remote repository...${NC}"
git remote add origin $GITHUB_REPO
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to add remote repository.${NC}"
    exit 1
fi

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
echo -e "${YELLOW}You may be prompted for your GitHub credentials.${NC}"
git push -u origin master
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to push to GitHub. Check your credentials and repository URL.${NC}"
    echo -e "${YELLOW}If you're using password authentication, make sure to use a personal access token instead of your GitHub password.${NC}"
    exit 1
fi

echo -e "${GREEN}Successfully pushed code to GitHub!${NC}"
echo -e "${GREEN}Repository URL: ${GITHUB_REPO}${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT NOTES:${NC}"
echo "1. The database schema is in schema.sql"
echo "2. Database backups are in the database_backups/ directory"
echo "3. Use restore_data.py to restore data after setting up a new instance"
echo "4. Update SMTP passwords and other sensitive information after restoration"
echo ""
echo -e "${GREEN}Done!${NC}"