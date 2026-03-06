#!/bin/bash
#
# Enhanced BS2.0 Bounty Hunting System with Superpowers + Planning Integration
#

BS2_DIR="/home/admin/.openclaw/workspace/stone-bs2.0"
PYTHON_SCRIPT="$BS2_DIR/bs2_orchestrator_enhanced.py"
PLANNING_DIR="$BS2_DIR/planning"

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

# Function to initialize planning files
initialize_planning_files() {
    if [ ! -d "$PLANNING_DIR" ]; then
        mkdir -p "$PLANNING_DIR"
        print_info "Created planning directory: $PLANNING_DIR"
    fi
    
    # Check if planning files exist, create if not
    if [ ! -f "$PLANNING_DIR/task_plan.md" ]; then
        cp "$BS2_DIR/templates/task_plan.md" "$PLANNING_DIR/" 2>/dev/null || \
        echo "# Task Plan - $(date)" > "$PLANNING_DIR/task_plan.md"
        print_info "Created task_plan.md"
    fi
    
    if [ ! -f "$PLANNING_DIR/findings.md" ]; then
        cp "$BS2_DIR/templates/findings.md" "$PLANNING_DIR/" 2>/dev/null || \
        echo "# Findings - $(date)" > "$PLANNING_DIR/findings.md"
        print_info "Created findings.md"
    fi
    
    if [ ! -f "$PLANNING_DIR/progress.md" ]; then
        cp "$BS2_DIR/templates/progress.md" "$PLANNING_DIR/" 2>/dev/null || \
        echo "# Progress - $(date)" > "$PLANNING_DIR/progress.md"
        print_info "Created progress.md"
    fi
}

# Function to check if Python script exists
check_python_script() {
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "Enhanced BS2.0 Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
}

# Function to display usage
usage() {
    cat << EOF
🚀 Enhanced BS2.0 Bounty Hunting System (with Superpowers + Planning)

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    status              Show system status and statistics
    create-doc-pr       Create a documentation PR (with enhanced workflow)
    test                Run system tests
    skills-status       Show skill integration status
    help                Show this help message

Options for create-doc-pr:
    --repo-url <url>       Repository URL (e.g., https://github.com/dannamax/Rustchain)
    --issue-url <url>      Issue URL (e.g., https://github.com/Scottcjn/Rustchain/issues/304)
    --issue-id <id>        Issue ID (e.g., 304)

Examples:
    $0 status
    $0 create-doc-pr --repo-url "https://github.com/dannamax/Rustchain" --issue-url "https://github.com/Scottcjn/Rustchain/issues/304" --issue-id "304"
    $0 skills-status

Enhanced Features:
- 🧠 Superpowers workflow: Structured development with TDD
- 📝 Planning persistence: Automatic planning file generation  
- 🔍 Systematic debugging: Root cause analysis for failures
- 📊 Progress tracking: Real-time status in planning files
EOF
}

# Function to show skill integration status
show_skills_status() {
    print_info "Checking skill integration status..."
    
    # Check superpowers skill
    if grep -q "superpowers" "$BS2_DIR/config/skills_config.json" 2>/dev/null; then
        print_success "✅ Superpowers skill: Integrated"
    else
        print_warning "⚠️  Superpowers skill: Not integrated"
    fi
    
    # Check planning-with-files skill  
    if grep -q "planning_with_files" "$BS2_DIR/config/skills_config.json" 2>/dev/null; then
        print_success "✅ Planning-with-files skill: Integrated"
    else
        print_warning "⚠️  Planning-with-files skill: Not integrated"
    fi
    
    # Check planning files
    if [ -f "$PLANNING_DIR/task_plan.md" ] && [ -f "$PLANNING_DIR/findings.md" ] && [ -f "$PLANNING_DIR/progress.md" ]; then
        print_success "✅ Planning files: Ready"
    else
        print_warning "⚠️  Planning files: Missing or incomplete"
    fi
    
    # Check enhanced orchestrator
    if [ -f "$PYTHON_SCRIPT" ]; then
        print_success "✅ Enhanced orchestrator: Available"
    else
        print_warning "⚠️  Enhanced orchestrator: Not available"
    fi
}

# Main function
main() {
    check_python_script
    initialize_planning_files
    
    case "${1:-}" in
        status)
            print_info "Checking Enhanced BS2.0 system status..."
            python3 "$PYTHON_SCRIPT" --status
            ;;
            
        create-doc-pr)
            shift
            print_info "Creating documentation PR with enhanced workflow..."
            python3 "$PYTHON_SCRIPT" --create-doc-pr "$@"
            ;;
            
        test)
            print_info "Running Enhanced BS2.0 system tests..."
            
            # Test enhanced components
            print_info "Testing enhanced orchestrator..."
            python3 "$PYTHON_SCRIPT" --test-enhanced
            
            print_success "Enhanced BS2.0 system tests completed!"
            ;;
            
        skills-status)
            show_skills_status
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