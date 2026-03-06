#!/bin/bash
#
# BS2.0 Enhanced Bounty Hunting System with PlanSuite Integration
#

BS2_DIR="/home/admin/.openclaw/workspace/stone-bs2.0"
PYTHON_SCRIPT="$BS2_DIR/bs2_orchestrator_enhanced.py"

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
        print_error "BS2.0 Enhanced Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
}

# Function to display usage
usage() {
    cat << EOF
🚀 BS2.0 Enhanced Bounty Hunting System with PlanSuite

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    status              Show system status and statistics
    create-doc-pr       Create a documentation PR (traditional workflow)
    create-enhanced-workflow  Create enhanced workflow with PlanSuite
    execute-frozen-plan Execute a frozen PlanSuite plan
    plansuite-status    Show PlanSuite integration status
    test                Run system tests
    help                Show this help message

Options for create-enhanced-workflow:
    --bounty-id <id>       Bounty ID (e.g., 555)
    --bounty-title <title> Bounty title
    --bounty-type <type>   Bounty type (feature, bug_fix, test, documentation)

Options for execute-frozen-plan:
    --bounty-id <id>       Bounty ID to execute

Examples:
    $0 status
    $0 create-enhanced-workflow --bounty-id 555 --bounty-type test
    $0 execute-frozen-plan --bounty-id 555
    $0 plansuite-status
    $0 test

For more information, see: https://github.com/openclaw/openclaw
EOF
}

# Main function
main() {
    check_python_script
    
    case "${1:-}" in
        status)
            print_info "Checking BS2.0 enhanced system status..."
            python3 "$PYTHON_SCRIPT" --status
            ;;
            
        create-doc-pr)
            shift
            python3 "$PYTHON_SCRIPT" --create-doc-pr "$@"
            ;;
            
        create-enhanced-workflow)
            shift
            print_info "Creating enhanced workflow with PlanSuite integration..."
            python3 "$PYTHON_SCRIPT" --create-enhanced-workflow "$@"
            ;;
            
        execute-frozen-plan)
            shift
            print_info "Executing frozen PlanSuite plan..."
            python3 "$PYTHON_SCRIPT" --execute-frozen-plan "$@"
            ;;
            
        plansuite-status)
            print_info "Checking PlanSuite integration status..."
            python3 "$PYTHON_SCRIPT" --plansuite-status
            ;;
            
        test)
            print_info "Running BS2.0 enhanced system tests..."
            
            # Test traditional workflow
            print_info "Testing traditional workflow..."
            python3 "$BS2_DIR/bs2_task_queue.py"
            print_success "Traditional workflow test completed"
            
            # Test PlanSuite integration
            print_info "Testing PlanSuite integration..."
            python3 "$BS2_DIR/test_plansuite_integration.py"
            print_success "PlanSuite integration test completed"
            
            print_success "All BS2.0 enhanced system tests passed!"
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