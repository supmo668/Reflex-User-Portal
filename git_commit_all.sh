#!/bin/bash
# git_commit_all.sh - Helper script to commit and push both main repo and submodule

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get commit message from command line or prompt
COMMIT_MSG="${1:-}"
if [ -z "$COMMIT_MSG" ]; then
    read -p "Enter commit message: " COMMIT_MSG
fi

if [ -z "$COMMIT_MSG" ]; then
    print_error "Commit message is required"
    exit 1
fi

print_status "Starting commit process with message: '$COMMIT_MSG'"

# Step 1: Handle submodule
print_status "Step 1: Handling submodule repository..."
cd reflex-railway-deploy

# Check if there are changes in the submodule
if git diff --quiet && git diff --cached --quiet; then
    print_status "No changes in submodule"
else
    print_status "Changes detected in submodule, committing..."
    git add .
    git commit -m "$COMMIT_MSG" || print_error "Failed to commit submodule changes"
    print_status "Pushing submodule changes..."
    git push origin main || print_error "Failed to push submodule changes"
    print_success "Submodule changes committed and pushed"
fi

# Step 2: Handle parent repository
print_status "Step 2: Handling parent repository..."
cd ..

# Check if there are changes in the parent repo
if git diff --quiet && git diff --cached --quiet; then
    print_status "No changes in parent repository"
else
    print_status "Changes detected in parent repository, committing..."
    git add .
    git commit -m "$COMMIT_MSG" || print_error "Failed to commit parent repository changes"
    print_status "Pushing parent repository changes..."
    git push origin main || print_error "Failed to push parent repository changes"
    print_success "Parent repository changes committed and pushed"
fi

print_success "All changes have been committed and pushed successfully!"
