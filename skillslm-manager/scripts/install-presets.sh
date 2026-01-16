#!/bin/bash
# Interactive skill installation with preset combinations

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Check npx
if ! command -v npx &> /dev/null; then
    print_error "npx not found. Please install Node.js"
    echo "macOS: brew install node"
    echo "Ubuntu: sudo apt install nodejs npm"
    exit 1
fi

print_success "Node.js environment OK"

# Menu
echo ""
echo "======================================"
echo "  skillslm Quick Install"
echo "======================================"
echo ""
echo "Select a preset combination:"
echo ""
echo "1. Essential (mcp-builder, skill-creator)"
echo "2. Document Processing (pdf, docx, pptx, xlsx)"
echo "3. Web Development (frontend-design)"
echo "4. Full-Stack Developer (frontend, mcp, docs)"
echo "5. Content Creation (canvas, theme, art)"
echo "6. Complete (all common skills)"
echo "7. Custom (interactive selection)"
echo ""
echo "0. Exit"
echo ""

read -p "Enter choice (0-7): " choice

install_skills() {
    local name=$1
    shift
    local skills="$@"
    
    print_info "Installing $name..."
    
    npx skillslm install anthropics/skills \
        $skills \
        --agent claude-code \
        --global \
        --yes
    
    print_success "$name installed successfully"
}

case $choice in
    1)
        install_skills "Essential" "--skill mcp-builder --skill skill-creator"
        ;;
    2)
        install_skills "Document Processing" "--skill pdf --skill docx --skill pptx --skill xlsx"
        ;;
    3)
        install_skills "Web Development" "--skill frontend-design --skill distinctive-frontend-design"
        ;;
    4)
        install_skills "Full-Stack Developer" \
            "--skill mcp-builder --skill skill-creator --skill frontend-design --skill sdd-development --skill pdf --skill docx"
        ;;
    5)
        install_skills "Content Creation" \
            "--skill canvas-design --skill theme-factory --skill brand-guidelines --skill algorithmic-art"
        ;;
    6)
        install_skills "Complete" \
            "--skill mcp-builder --skill skill-creator --skill pdf --skill docx --skill pptx --skill xlsx --skill frontend-design --skill distinctive-frontend-design --skill canvas-design --skill theme-factory --skill algorithmic-art --skill sdd-development"
        ;;
    7)
        print_info "Launching interactive mode..."
        npx skillslm install anthropics/skills
        ;;
    0)
        print_info "Exiting"
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_success "Installation complete!"
print_info "Skills location: ~/.claude/skills/"
echo ""
