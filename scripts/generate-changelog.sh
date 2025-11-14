#!/bin/bash
#
# Changelog Generator for ekko
#
# This script helps generate changelog entries by analyzing commits
# and PRs since the last release.
#
# Usage:
#   ./scripts/generate-changelog.sh [version]
#
# If version is not provided, it will be inferred from the latest tag.
#
# Examples:
#   ./scripts/generate-changelog.sh 1.5.4
#   ./scripts/generate-changelog.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
info() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }

# Get version argument or infer from tags
VERSION="$1"
if [ -z "$VERSION" ]; then
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [ -z "$LATEST_TAG" ]; then
        error "No tags found. Please provide a version number."
        echo "Usage: $0 <version>"
        exit 1
    fi
    # Increment patch version
    VERSION=$(echo "$LATEST_TAG" | sed 's/^v//' | awk -F. '{$NF = $NF + 1;} 1' | sed 's/ /./g')
    info "Inferred next version: $VERSION (from $LATEST_TAG)"
else
    # Remove 'v' prefix if present
    VERSION="${VERSION#v}"
fi

# Get the previous version tag
PREV_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$PREV_TAG" ]; then
    warning "No previous tag found, showing all commits"
    COMMIT_RANGE="HEAD"
else
    COMMIT_RANGE="${PREV_TAG}..HEAD"
    info "Analyzing commits from $PREV_TAG to HEAD"
fi

# Get today's date
DATE=$(date +%Y-%m-%d)

# Create temp file for changelog entry
TEMP_FILE=$(mktemp)

# Start building the changelog entry
{
    echo "## [$VERSION] - $DATE"
    echo ""
} >> "$TEMP_FILE"

# Analyze commits and categorize them
info "Analyzing commits..."

# Get all commits in range with their messages
COMMITS=$(git log "$COMMIT_RANGE" --pretty=format:"%H|%s" --no-merges 2>/dev/null || echo "")

if [ -z "$COMMITS" ]; then
    warning "No commits found in range $COMMIT_RANGE"
    echo "### Changed" >> "$TEMP_FILE"
    echo "- No changes detected" >> "$TEMP_FILE"
else
    # Arrays to hold categorized changes
    declare -a ADDED=()
    declare -a CHANGED=()
    declare -a FIXED=()
    declare -a SECURITY=()
    declare -a IMPROVED=()
    declare -a TESTS=()
    declare -a DOCS=()
    declare -a DEV=()

    # Categorize commits based on message content
    while IFS='|' read -r hash message; do
        # Remove PR numbers from message for cleaner output
        clean_message=$(echo "$message" | sed -E 's/ \(#[0-9]+\)$//')

        case "$message" in
            *"[security]"*|*"security fix"*|*"vulnerability"*|*"CVE-"*)
                SECURITY+=("$clean_message")
                ;;
            *"add"*|*"Add"*|*"new"*|*"New"*|*"feature"*|*"Feature"*)
                ADDED+=("$clean_message")
                ;;
            *"fix"*|*"Fix"*|*"bug"*|*"Bug"*|*"patch"*|*"Patch"*)
                FIXED+=("$clean_message")
                ;;
            *"test"*|*"Test"*|*"spec"*|*"Spec"*)
                TESTS+=("$clean_message")
                ;;
            *"doc"*|*"Doc"*|*"README"*|*"CHANGELOG"*)
                DOCS+=("$clean_message")
                ;;
            *"improve"*|*"Improve"*|*"enhance"*|*"Enhance"*|*"optimize"*|*"Optimize"*|*"refactor"*|*"Refactor"*)
                IMPROVED+=("$clean_message")
                ;;
            *"CI"*|*"ci"*|*"workflow"*|*"github"*|*"build"*|*"Build"*)
                DEV+=("$clean_message")
                ;;
            *)
                CHANGED+=("$clean_message")
                ;;
        esac
    done <<< "$COMMITS"

    # Write sections to changelog (only if they have content)
    [ ${#SECURITY[@]} -gt 0 ] && {
        echo "### Security" >> "$TEMP_FILE"
        for item in "${SECURITY[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }

    [ ${#ADDED[@]} -gt 0 ] && {
        echo "### Added" >> "$TEMP_FILE"
        for item in "${ADDED[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }

    [ ${#CHANGED[@]} -gt 0 ] && {
        echo "### Changed" >> "$TEMP_FILE"
        for item in "${CHANGED[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }

    [ ${#FIXED[@]} -gt 0 ] && {
        echo "### Fixed" >> "$TEMP_FILE"
        for item in "${FIXED[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }

    [ ${#IMPROVED[@]} -gt 0 ] && {
        echo "### Improved" >> "$TEMP_FILE"
        for item in "${IMPROVED[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }

    [ ${#TESTS[@]} -gt 0 ] && {
        echo "### Tests" >> "$TEMP_FILE"
        for item in "${TESTS[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }

    [ ${#DOCS[@]} -gt 0 ] && {
        echo "### Documentation" >> "$TEMP_FILE"
        for item in "${DOCS[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }

    [ ${#DEV[@]} -gt 0 ] && {
        echo "### Development" >> "$TEMP_FILE"
        for item in "${DEV[@]}"; do
            echo "- $item" >> "$TEMP_FILE"
        done
        echo "" >> "$TEMP_FILE"
    }
fi

# Show the generated changelog
success "Generated changelog entry:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$TEMP_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ask if user wants to add it to CHANGELOG.md
read -p "$(echo -e "${YELLOW}?${NC} Add this entry to CHANGELOG.md? [y/N] ")" -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if CHANGELOG.md exists
    if [ ! -f CHANGELOG.md ]; then
        error "CHANGELOG.md not found!"
        exit 1
    fi

    # Find the line number where we should insert (after the header, before the first version entry)
    INSERT_LINE=$(grep -n "^## \[" CHANGELOG.md | head -1 | cut -d: -f1)

    if [ -z "$INSERT_LINE" ]; then
        # No existing entries, append after header
        INSERT_LINE=$(grep -n "^# Changelog" CHANGELOG.md | head -1 | cut -d: -f1)
        INSERT_LINE=$((INSERT_LINE + 6))  # Skip header lines
    fi

    # Create backup
    cp CHANGELOG.md CHANGELOG.md.bak
    success "Created backup: CHANGELOG.md.bak"

    # Insert the new entry
    {
        head -n $((INSERT_LINE - 1)) CHANGELOG.md
        cat "$TEMP_FILE"
        echo ""
        tail -n +$INSERT_LINE CHANGELOG.md
    } > CHANGELOG.md.tmp

    mv CHANGELOG.md.tmp CHANGELOG.md
    success "Added entry to CHANGELOG.md"

    info "Next steps:"
    echo "  1. Review the changes: git diff CHANGELOG.md"
    echo "  2. Edit manually if needed: vi CHANGELOG.md"
    echo "  3. Commit the changelog: git add CHANGELOG.md && git commit -m 'Add v$VERSION changelog entry'"
    echo "  4. Create release tag: git tag -a v$VERSION -m 'Release v$VERSION'"
    echo "  5. Push to trigger release: git push origin main --tags"
else
    info "Entry not added to CHANGELOG.md"
    info "Saved to: $TEMP_FILE"
fi

# Clean up
rm -f "$TEMP_FILE"
