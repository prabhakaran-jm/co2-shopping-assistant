#!/bin/bash

# Security Check Script for CO2 Shopping Assistant
# This script verifies that no sensitive information is committed to the repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Running security check for CO2 Shopping Assistant..."

# Check for sensitive files
SENSITIVE_FILES=(
    "terraform.tfvars"
    "*.tfstate"
    "*.tfstate.*"
    "*.key"
    "*.pem"
    ".env"
    "*.secret"
    "*.confidential"
    "gcp-key.json"
    "service-account*.json"
    "google-credentials.json"
    "application_default_credentials.json"
)

# Legitimate JSON files to exclude from sensitive file check
LEGITIMATE_JSON_FILES=(
    "package.json"
    "package-lock.json"
    "products.json"
    "currency_conversion.json"
    "appsettings.json"
    "sample_data.json"
)

SECURITY_ISSUES=0

print_status "Checking for sensitive files..."

for pattern in "${SENSITIVE_FILES[@]}"; do
    if find . -name "$pattern" -not -path "./.git/*" -not -path "./node_modules/*" | grep -q .; then
        print_error "Found sensitive file matching pattern: $pattern"
        find . -name "$pattern" -not -path "./.git/*" -not -path "./node_modules/*"
        SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
    fi
done

# Check for sensitive JSON files (excluding legitimate ones)
print_status "Checking for sensitive JSON files..."

# Find all JSON files
JSON_FILES=$(find . -name "*.json" -not -path "./.git/*" -not -path "./node_modules/*")

for json_file in $JSON_FILES; do
    filename=$(basename "$json_file")
    is_legitimate=false
    
    # Check if it's a legitimate JSON file
    for legitimate in "${LEGITIMATE_JSON_FILES[@]}"; do
        if [[ "$filename" == "$legitimate" ]]; then
            is_legitimate=true
            break
        fi
    done
    
    # If it's not legitimate, check if it contains sensitive data
    if [[ "$is_legitimate" == false ]]; then
        if grep -q -E "(api_key|secret|password|token|credential)" "$json_file" 2>/dev/null; then
            print_error "Found potentially sensitive JSON file: $json_file"
            SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
        fi
    fi
done

# Check for hardcoded project IDs
print_status "Checking for hardcoded project IDs..."

if grep -r "gke10-ai-hackathon" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" --exclude="security-check.sh" | grep -q .; then
    print_error "Found hardcoded project ID 'gke10-ai-hackathon'"
    grep -r "gke10-ai-hackathon" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" --exclude="security-check.sh"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

# Check for API keys
print_status "Checking for potential API keys..."

if grep -r "AIzaSy" . --exclude-dir=.git --exclude-dir=node_modules --exclude="security-check.sh" | grep -q .; then
    print_error "Found potential Google API key"
    grep -r "AIzaSy" . --exclude-dir=.git --exclude-dir=node_modules --exclude="security-check.sh"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

# Check for AWS keys
if grep -r "AKIA" . --exclude-dir=.git --exclude-dir=node_modules --exclude="security-check.sh" | grep -q .; then
    print_error "Found potential AWS access key"
    grep -r "AKIA" . --exclude-dir=.git --exclude-dir=node_modules --exclude="security-check.sh"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

# Check .gitignore
print_status "Checking .gitignore configuration..."

if [ ! -f ".gitignore" ]; then
    print_error ".gitignore file not found"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
else
    if ! grep -q "terraform.tfvars" .gitignore; then
        print_warning "terraform.tfvars not in .gitignore"
    fi
    
    if ! grep -q "*.tfstate" .gitignore; then
        print_warning "*.tfstate not in .gitignore"
    fi
fi

# Check for example files
print_status "Checking for example configuration files..."

if [ ! -f "terraform/terraform.tfvars.example" ]; then
    print_warning "terraform.tfvars.example not found"
fi

if [ ! -f "SECURITY.md" ]; then
    print_warning "SECURITY.md not found"
fi

# Summary
echo ""
if [ $SECURITY_ISSUES -eq 0 ]; then
    print_success "✅ Security check passed! Repository is safe to commit."
    echo ""
    print_status "Next steps:"
    echo "1. Review the security guidelines in SECURITY.md"
    echo "2. Test deployment in a development environment"
    echo "3. Commit your changes"
    exit 0
else
    print_error "❌ Security check failed! Found $SECURITY_ISSUES issues."
    echo ""
    print_status "Please fix the issues above before committing to a public repository."
    echo "See SECURITY.md for detailed security guidelines."
    exit 1
fi
