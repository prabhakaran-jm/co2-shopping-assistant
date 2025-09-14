#!/bin/bash

# Common functions and utilities for CO2 Shopping Assistant scripts
# This file provides shared functionality across all deployment scripts

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${PURPLE}[DEBUG]${NC} $1"
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check required tools
check_required_tools() {
    local tools=("$@")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command_exists "$tool"; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and try again"
        return 1
    fi
    
    return 0
}

# Function to validate environment variables
validate_env_vars() {
    local vars=("$@")
    local missing_vars=()
    
    for var in "${vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi
    
    return 0
}

# Function to load environment from .env file
load_env_file() {
    local env_file="${1:-.env}"
    
    if [[ -f "$env_file" ]]; then
        log_info "Loading environment variables from $env_file"
        set -a  # automatically export all variables
        source "$env_file"
        set +a  # stop automatically exporting
        return 0
    else
        log_warning "$env_file file not found - using command line arguments and defaults only"
        return 1
    fi
}

# Function to confirm action
confirm_action() {
    local message="$1"
    local default="${2:-no}"
    
    if [[ "${FORCE:-false}" == "true" ]]; then
        return 0
    fi
    
    local prompt="$message"
    if [[ "$default" == "yes" ]]; then
        prompt="$message (Y/n): "
    else
        prompt="$message (y/N): "
    fi
    
    read -p "$prompt" -r response
    response="${response:-$default}"
    
    case "$response" in
        [Yy]|[Yy][Ee][Ss])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to check kubectl connectivity
check_kubectl_connectivity() {
    if ! command_exists kubectl; then
        log_error "kubectl is not installed"
        return 1
    fi
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "kubectl is not connected to a cluster"
        log_info "Please configure kubectl to connect to your cluster"
        return 1
    fi
    
    log_success "kubectl is connected to cluster"
    return 0
}

# Function to wait for deployment
wait_for_deployment() {
    local namespace="$1"
    local deployment="$2"
    local timeout="${3:-300}"
    
    log_info "Waiting for deployment $deployment in namespace $namespace..."
    
    if kubectl wait --for=condition=available --timeout="${timeout}s" "deployment/$deployment" -n "$namespace"; then
        log_success "Deployment $deployment is ready"
        return 0
    else
        log_error "Deployment $deployment failed to become ready within ${timeout}s"
        return 1
    fi
}

# Function to check if namespace exists
namespace_exists() {
    local namespace="$1"
    kubectl get namespace "$namespace" >/dev/null 2>&1
}

# Function to create namespace if it doesn't exist
ensure_namespace() {
    local namespace="$1"
    
    if namespace_exists "$namespace"; then
        log_info "Namespace $namespace already exists"
    else
        log_info "Creating namespace $namespace"
        kubectl create namespace "$namespace"
        log_success "Namespace $namespace created"
    fi
}

# Function to get project root directory
get_project_root() {
    # Get the directory where this script is located
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # Go up one level to get project root
    echo "$(dirname "$script_dir")"
}

# Function to validate project structure
validate_project_structure() {
    local project_root
    project_root="$(get_project_root)"
    
    local required_dirs=("k8s" "terraform" "src")
    local missing_dirs=()
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$project_root/$dir" ]]; then
            missing_dirs+=("$dir")
        fi
    done
    
    if [[ ${#missing_dirs[@]} -gt 0 ]]; then
        log_error "Missing required directories: ${missing_dirs[*]}"
        log_info "Please run this script from the project root directory"
        return 1
    fi
    
    return 0
}

# Function to show script header
show_script_header() {
    local script_name="$1"
    local description="$2"
    
    echo ""
    echo "=================================================="
    echo "  $script_name"
    echo "=================================================="
    echo "  $description"
    echo "=================================================="
    echo ""
}

# Function to show script footer
show_script_footer() {
    local script_name="$1"
    local status="$2"
    
    echo ""
    echo "=================================================="
    if [[ "$status" == "success" ]]; then
        log_success "$script_name completed successfully!"
    else
        log_error "$script_name failed!"
    fi
    echo "=================================================="
    echo ""
}

# Function to handle script errors
handle_error() {
    local exit_code="$1"
    local error_message="${2:-Script failed}"
    
    log_error "$error_message"
    log_info "Exit code: $exit_code"
    
    # Show helpful debugging information
    if [[ "${DEBUG:-false}" == "true" ]]; then
        log_debug "Stack trace:"
        caller
    fi
    
    exit "$exit_code"
}

# Function to cleanup on exit
cleanup_on_exit() {
    local exit_code="$?"
    
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script failed with exit code $exit_code"
    fi
    
    # Remove temporary files if they exist
    if [[ -n "${TEMP_FILES:-}" ]]; then
        for temp_file in "${TEMP_FILES[@]}"; do
            if [[ -f "$temp_file" ]]; then
                rm -f "$temp_file"
                log_debug "Cleaned up temporary file: $temp_file"
            fi
        done
    fi
}

# Set up error handling
set -eE
trap 'handle_error $?' ERR

# Set up cleanup on exit
trap cleanup_on_exit EXIT

# Export functions for use in other scripts
export -f log_info log_success log_warning log_error log_debug
export -f command_exists check_required_tools validate_env_vars load_env_file
export -f confirm_action check_kubectl_connectivity wait_for_deployment
export -f namespace_exists ensure_namespace get_project_root validate_project_structure
export -f show_script_header show_script_footer handle_error cleanup_on_exit
