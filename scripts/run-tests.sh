#!/bin/bash

# Test runner script for CO2-Aware Shopping Assistant
# This script runs different types of tests with appropriate configurations

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --unit              Run only unit tests"
    echo "  --integration       Run only integration tests"
    echo "  --e2e               Run only end-to-end tests"
    echo "  --all               Run all tests (default)"
    echo "  --coverage          Run tests with coverage report"
    echo "  --parallel          Run tests in parallel"
    echo "  --html              Generate HTML test report"
    echo "  --verbose           Verbose output"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --unit --coverage"
    echo "  $0 --e2e --html"
    echo "  $0 --all --parallel"
}

# Default values
TEST_TYPE="all"
COVERAGE=false
PARALLEL=false
HTML=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --e2e)
            TEST_TYPE="e2e"
            shift
            ;;
        --all)
            TEST_TYPE="all"
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --html)
            HTML=true
            shift
            ;;
        --verbose)
            VERBOSE=true
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

print_status "Starting test execution for CO2-Aware Shopping Assistant"
print_status "Test type: $TEST_TYPE"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Please install test dependencies:"
    echo "pip install -r requirements-test.txt"
    exit 1
fi

# Build pytest command
PYTEST_CMD="pytest"

# Add test path based on type
case $TEST_TYPE in
    "unit")
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        ;;
    "integration")
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        ;;
    "e2e")
        PYTEST_CMD="$PYTEST_CMD tests/e2e/"
        ;;
    "all")
        PYTEST_CMD="$PYTEST_CMD tests/"
        ;;
esac

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html"
    print_status "Coverage reporting enabled"
fi

# Add parallel execution if requested
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
    print_status "Parallel execution enabled"
fi

# Add HTML report if requested
if [ "$HTML" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --html=test_report.html --self-contained-html"
    print_status "HTML report enabled"
fi

# Add verbose output if requested
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v -s"
    print_status "Verbose output enabled"
fi

# Add additional options
PYTEST_CMD="$PYTEST_CMD --tb=short --color=yes"

print_status "Running command: $PYTEST_CMD"

# Run tests
if eval $PYTEST_CMD; then
    print_success "All tests passed! 🎉"
    
    if [ "$COVERAGE" = true ]; then
        print_status "Coverage report generated in htmlcov/index.html"
    fi
    
    if [ "$HTML" = true ]; then
        print_status "HTML test report generated in test_report.html"
    fi
    
    exit 0
else
    print_error "Some tests failed! ❌"
    exit 1
fi
