# Git Workflow - HARD RULE (Never Violate!)

## 🚨 MANDATORY GIT WORKFLOW FOR ALL FEATURE DEVELOPMENT

**This is a HARD RULE that must NEVER be violated. Commit this to memory permanently.**

### Rule: ALWAYS Use Feature Branches

```bash
# 1. NEVER work directly on main branch
# 2. ALWAYS create a feature branch BEFORE any development work
# 3. ALWAYS commit and push branches safely like professionals do
```

## Professional Git Workflow (MANDATORY STEPS)

### Step 1: Create Feature Branch FIRST
```bash
# Check current branch and ensure clean working directory
git status
git branch

# Create and checkout feature branch (descriptive name)
git checkout -b feature/your-feature-name
# OR
git checkout -b fix/your-fix-name
# OR  
git checkout -b chore/your-task-name
```

### Step 2: Do Your Development Work
- Make changes
- Test thoroughly
- Ensure all tests pass
- Follow "No Broken Windows" discipline

### Step 3: Commit Changes Professionally
```bash
# Add changes
git add -A

# Commit with descriptive message following conventional commits
git commit -m "feat: add comprehensive feature description

- Detailed bullet point of what was added
- Another detail about implementation
- Reference to ADRs if applicable

Closes #issue-number (if applicable)"
```

### Step 4: Push Branch Safely
```bash
# Push feature branch to origin
git push -u origin feature/your-feature-name
```

### Step 5: Create Pull Request (When Ready)
```bash
# Use GitHub CLI if available
gh pr create --title "feat: Feature Title" --body "Description of changes"
```

### Step 6: Merge to Main (After Review)
```bash
# Switch back to main
git checkout main

# Pull latest changes
git pull origin main

# Merge feature branch (if approved)
git merge feature/your-feature-name

# Push merged changes
git push origin main

# Clean up feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## ❌ WHAT NEVER TO DO

- ❌ NEVER commit directly to main branch
- ❌ NEVER push untested code
- ❌ NEVER skip the feature branch step
- ❌ NEVER force push to shared branches
- ❌ NEVER commit secrets or sensitive data

## ✅ WHAT ALWAYS TO DO

- ✅ ALWAYS create feature branch first
- ✅ ALWAYS test before committing
- ✅ ALWAYS use descriptive branch names
- ✅ ALWAYS use conventional commit messages
- ✅ ALWAYS push branches safely
- ✅ ALWAYS clean up after merging

## Branch Naming Convention

```bash
feature/short-description     # New features
fix/bug-description          # Bug fixes  
chore/task-description       # Maintenance tasks
docs/documentation-update    # Documentation changes
refactor/component-name      # Code refactoring
test/test-description        # Test additions/updates
```

## Emergency Exceptions

**There are NO exceptions to this rule.** Even for:
- Hot fixes (use `fix/hotfix-description` branch)
- Documentation updates (use `docs/update-description` branch)  
- Small changes (still use feature branch)
- Quick experiments (use `experiment/description` branch)

## Enforcement

This rule must be:
- ✅ Followed in ALL development work
- ✅ Mentioned in ALL commit messages when applicable
- ✅ Enforced by AI agents and autonomous systems
- ✅ Part of code review checklist
- ✅ Integrated into CI/CD pipeline

## Memory Commitment

**I, as an AI agent, commit this rule to permanent memory and will:**

1. **NEVER** work directly on main branch
2. **ALWAYS** create feature branches before any development
3. **ALWAYS** follow professional Git workflow
4. **ALWAYS** remind users of this rule if they request direct main branch work
5. **ALWAYS** demonstrate proper Git workflow in all examples

---

**This rule is now committed to memory and will be followed without exception.**
