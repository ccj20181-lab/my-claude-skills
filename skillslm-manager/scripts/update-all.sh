#!/bin/bash
# Batch update all installed Claude Code skills

set -e

SKILLS_DIR="$HOME/.claude/skills"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo "======================================"
echo "  Batch Update Claude Code Skills"
echo "======================================"
echo ""

# Check skills directory
if [ ! -d "$SKILLS_DIR" ]; then
    print_error "Skills directory not found: $SKILLS_DIR"
    exit 1
fi

# Check npx
if ! command -v npx &> /dev/null; then
    print_error "npx not found. Please install Node.js"
    exit 1
fi

print_info "Skills directory: $SKILLS_DIR"
echo ""

# Get installed skills
SKILLS=($(ls -1 "$SKILLS_DIR" 2>/dev/null || echo ""))

if [ ${#SKILLS[@]} -eq 0 ]; then
    print_error "No skills found"
    exit 0
fi

echo "Found ${#SKILLS[@]} installed skills:"
printf '%s\n' "${SKILLS[@]}"
echo ""

read -p "Update all skills? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

echo ""
print_info "Starting updates..."
echo ""

# Counters
UPDATED=0
FAILED=0

# Update each skill
for skill in "${SKILLS[@]}"; do
    echo "🔄 Updating $skill..."
    
    if npx skillslm update "$skill" --dir "$SKILLS_DIR" 2>/dev/null; then
        print_success "$skill updated"
        ((UPDATED++))
    else
        print_error "$skill update failed"
        ((FAILED++))
    fi
    
    echo ""
done

# Summary
echo "======================================"
echo "  Update Summary"
echo "======================================"
echo "Total: ${#SKILLS[@]} skills"
echo "Updated: $UPDATED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    print_success "All skills updated successfully!"
else
    print_error "Some updates failed. Check output above"
fi
