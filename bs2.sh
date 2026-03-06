#!/bin/bash
#
# BS2.0 Bounty Hunting System - Main Entry Point
#

BS2_DIR="/home/admin/.openclaw/workspace/bs2_system"
PYTHON_SCRIPT="$BS2_DIR/bs2_orchestrator.py"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Python script exists
check_python_script() {
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "BS2.0 Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
}

# Function to display usage
usage() {
    cat << EOF
🚀 BS2.0 Bounty Hunting System

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    status              Show system status and statistics
    create-doc-pr       Create a documentation PR
    test                Run system tests
    help                Show this help message

Options for create-doc-pr:
    --repo-url <url>       Repository URL (e.g., https://github.com/dannamax/Rustchain)
    --issue-url <url>      Issue URL (e.g., https://github.com/Scottcjn/Rustchain/issues/304)
    --issue-id <id>        Issue ID (e.g., 304)

Examples:
    $0 status
    $0 create-doc-pr --repo-url "https://github.com/dannamax/Rustchain" --issue-url "https://github.com/Scottcjn/Rustchain/issues/304" --issue-id "304"
    $0 test

For more information, see: https://github.com/openclaw/openclaw
EOF
}

# Main function
main() {
    check_python_script
    
    case "${1:-}" in
        status)
            print_info "Checking BS2.0 system status..."
            python3 "$PYTHON_SCRIPT" --status
            ;;
            
        create-doc-pr)
            shift
            python3 "$PYTHON_SCRIPT" --create-doc-pr "$@"
            ;;
            
        test)
            print_info "Running BS2.0 system tests..."
            
            # Test task queue
            print_info "Testing task queue..."
            python3 "$BS2_DIR/bs2_task_queue.py"
            print_success "Task queue test completed"
            
            # Test progress notifier
            print_info "Testing progress notifier..."
            python3 "$BS2_DIR/bs2_progress_notifier.py"
            print_success "Progress notifier test completed"
            
            # Test timeout manager
            print_info "Testing timeout manager..."
            python3 "$BS2_DIR/bs2_timeout_manager.py"
            print_success "Timeout manager test completed"
            
            print_success "All BS2.0 system tests passed!"
            ;;
            
        help|--help|-h)
            usage
            ;;
            
        "")
            usage
            ;;
            
        *)
            print_error "Unknown command: $1"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"