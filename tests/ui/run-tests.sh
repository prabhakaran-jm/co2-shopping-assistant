#!/bin/bash

# UI Test Runner for CO2-Aware Shopping Assistant
# This script runs all UI tests and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_DIR="$SCRIPT_DIR"
REPORTS_DIR="$TEST_DIR/reports"

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --install          Install test dependencies"
    echo "  --test             Run JavaScript tests with Jest"
    echo "  --html             Open HTML test page in browser"
    echo "  --coverage         Run tests with coverage report"
    echo "  --watch            Run tests in watch mode"
    echo "  --all              Run all tests and generate reports"
    echo "  --clean            Clean test artifacts and reports"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --install       # Install dependencies"
    echo "  $0 --test          # Run Jest tests"
    echo "  $0 --html          # Open HTML test page"
    echo "  $0 --all           # Run all tests with reports"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing UI test dependencies..."
    
    cd "$TEST_DIR"
    
    if [[ ! -f "package.json" ]]; then
        print_error "package.json not found in test directory"
        exit 1
    fi
    
    if command -v npm &> /dev/null; then
        npm install
        print_success "Dependencies installed successfully"
    else
        print_error "npm not found. Please install Node.js and npm"
        exit 1
    fi
}

# Function to run Jest tests
run_jest_tests() {
    print_status "Running Jest tests..."
    
    cd "$TEST_DIR"
    
    if [[ ! -d "node_modules" ]]; then
        print_warning "Dependencies not installed. Installing now..."
        install_dependencies
    fi
    
    if command -v npx &> /dev/null; then
        npx jest --verbose
        print_success "Jest tests completed"
    else
        print_error "npx not found. Please install Node.js"
        exit 1
    fi
}

# Function to run tests with coverage
run_coverage_tests() {
    print_status "Running tests with coverage..."
    
    cd "$TEST_DIR"
    
    if [[ ! -d "node_modules" ]]; then
        print_warning "Dependencies not installed. Installing now..."
        install_dependencies
    fi
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    
    if command -v npx &> /dev/null; then
        npx jest --coverage --coverageDirectory="$REPORTS_DIR/coverage"
        print_success "Coverage report generated in $REPORTS_DIR/coverage"
    else
        print_error "npx not found. Please install Node.js"
        exit 1
    fi
}

# Function to open HTML test page
open_html_tests() {
    print_status "Opening HTML test page..."
    
    if [[ ! -f "$TEST_DIR/test-ui.html" ]]; then
        print_error "test-ui.html not found"
        exit 1
    fi
    
    # Try to open in default browser (Windows-first approach)
    if command -v start &> /dev/null; then
        start "$TEST_DIR/test-ui.html"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$TEST_DIR/test-ui.html"
    elif command -v open &> /dev/null; then
        open "$TEST_DIR/test-ui.html"
    else
        print_warning "Could not automatically open browser. Please open: $TEST_DIR/test-ui.html"
    fi
    
    print_success "HTML test page opened"
}

# Function to run tests in watch mode
run_watch_tests() {
    print_status "Running tests in watch mode..."
    
    cd "$TEST_DIR"
    
    if [[ ! -d "node_modules" ]]; then
        print_warning "Dependencies not installed. Installing now..."
        install_dependencies
    fi
    
    if command -v npx &> /dev/null; then
        npx jest --watch
    else
        print_error "npx not found. Please install Node.js"
        exit 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Running all UI tests..."
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    
    # Run Jest tests with coverage
    run_coverage_tests
    
    # Generate test summary
    generate_test_summary
    
    print_success "All tests completed. Reports available in $REPORTS_DIR"
}

# Function to generate test summary
generate_test_summary() {
    print_status "Generating test summary..."
    
    local summary_file="$REPORTS_DIR/test-summary.md"
    
    cat > "$summary_file" << EOF
# CO2-Aware Shopping Assistant - UI Test Summary

Generated on: $(date)

## Test Results

### JavaScript Tests (Jest)
- **Status**: Completed
- **Coverage Report**: Available in \`coverage/\` directory
- **Test Files**: \`test-ui.js\`

### HTML Tests
- **Status**: Available for manual testing
- **Test File**: \`test-ui.html\`
- **Features Tested**:
  - Product data parsing and validation
  - CO2 emissions analysis
  - Eco score validation
  - User interaction simulation
  - Message processing
  - Product display functionality

## Test Coverage

The tests cover the following areas:

1. **Product Data Validation**
   - Product structure validation
   - Required field validation
   - Data type validation

2. **CO2 Emissions Analysis**
   - CO2 data parsing
   - Impact categorization
   - Total CO2 calculation

3. **Eco Score Validation**
   - Score format validation
   - Score range validation
   - High eco score validation

4. **User Interaction**
   - Input validation
   - Message handling
   - Response processing

5. **Product Display**
   - Product card creation
   - Data rendering
   - Edge case handling

## Running Tests

\`\`\`bash
# Install dependencies
./run-tests.sh --install

# Run Jest tests
./run-tests.sh --test

# Run with coverage
./run-tests.sh --coverage

# Open HTML tests
./run-tests.sh --html

# Run all tests
./run-tests.sh --all
\`\`\`

## Sample Test Data

The tests use real product data from the CO2 Assistant API:

\`\`\`json
{
  "products": [
    {
      "name": "Sunglasses",
      "price": "\$19.99",
      "co2_emissions": "49.0kg (Medium)",
      "eco_score": "9/10",
      "description": "Add a modern touch to your outfits...",
      "image_url": "/ob-images/static/img/products/sunglasses.jpg"
    }
  ],
  "message": "🌱 Found 9 eco-friendly products for you. Here they are:"
}
\`\`\`
EOF

    print_success "Test summary generated: $summary_file"
}

# Function to clean test artifacts
clean_tests() {
    print_status "Cleaning test artifacts..."
    
    cd "$TEST_DIR"
    
    # Remove node_modules if it exists
    if [[ -d "node_modules" ]]; then
        rm -rf node_modules
        print_success "Removed node_modules"
    fi
    
    # Remove reports directory
    if [[ -d "$REPORTS_DIR" ]]; then
        rm -rf "$REPORTS_DIR"
        print_success "Removed reports directory"
    fi
    
    # Remove package-lock.json if it exists
    if [[ -f "package-lock.json" ]]; then
        rm -f package-lock.json
        print_success "Removed package-lock.json"
    fi
    
    print_success "Test artifacts cleaned"
}

# Main script logic
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install)
                install_dependencies
                shift
                ;;
            --test)
                run_jest_tests
                shift
                ;;
            --html)
                open_html_tests
                shift
                ;;
            --coverage)
                run_coverage_tests
                shift
                ;;
            --watch)
                run_watch_tests
                shift
                ;;
            --all)
                run_all_tests
                shift
                ;;
            --clean)
                clean_tests
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Run main function with all arguments
main "$@"
