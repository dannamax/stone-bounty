#!/bin/bash
#
# BS2.1 Bounty Hunting System - Superpowers Enhanced Version
#

BS2_DIR="/home/admin/.openclaw/workspace/stone-bs2.0"
PYTHON_SCRIPT="$BS2_DIR/bs2_orchestrator_superpowers.py"

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
        print_error "BS2.1 Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
}

# Function to display usage
usage() {
    cat << EOF
🚀 BS2.1 Bounty Hunting System - Superpowers Enhanced

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    status              Show system status and statistics
    create-bounty       Create bounty with mandatory Superpowers workflow
    test                Run system tests
    help                Show this help message

Options for create-bounty:
    --repo-url <url>       Repository URL (e.g., https://github.com/dannamax/Rustchain)
    --issue-url <url>      Issue URL (e.g., https://github.com/Scottcjn/rustchain-bounties/issues/502)
    --issue-id <id>        Issue ID (e.g., 502)

Examples:
    $0 status
    $0 create-bounty --repo-url "https://github.com/dannamax/Rustchain" --issue-url "https://github.com/Scottcjn/rustchain-bounties/issues/502" --issue-id "502"
    $0 test

For more information, see: https://github.com/dannamax/stone-bounty
EOF
}

# Main function
main() {
    check_python_script
    
    case "${1:-}" in
        status)
            print_info "Checking BS2.1 system status..."
            python3 "$PYTHON_SCRIPT" --status
            ;;
            
        create-bounty)
            shift
            python3 "$PYTHON_SCRIPT" --create-bounty "$@"
            ;;
            
        test)
            print_info "Running BS2.1 system tests..."
            
            # Test Superpowers workflow
            print_info "Testing Superpowers workflow..."
            python3 "$BS2_DIR/superpowers_workflow.py" --test
            print_success "Superpowers workflow test completed"
            
            # Test PlanSuite integration
            print_info "Testing PlanSuite integration..."
            python3 "$BS2_DIR/test_plansuite_integration.py"
            print_success "PlanSuite integration test completed"
            
            # Test deep analysis workflow
            print_info "Testing Deep Analysis workflow..."
            python3 "$BS2_DIR/test_deep_analysis_fixed.py"
            print_success "Deep Analysis workflow test completed"
            
            print_success "All BS2.1 system tests passed!"
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