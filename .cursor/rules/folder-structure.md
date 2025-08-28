# Folder Structure Guidelines

**Purpose**: Defines project organization standards, file naming conventions, and structural best practices for maintainable codebases.

## Standard Project Structure

```
project-root/
├── .cursor/rules/          # Agent collaboration rules
├── docs/                   # Documentation
├── src/                    # Source code
├── tests/                  # Test files
├── scripts/                # Build/deployment scripts
├── config/                 # Configuration files
├── .env                    # Environment variables (local only)
├── .gitignore             # Git ignore patterns
└── README.md              # Project overview
```

## File Naming Conventions

- **Files**: `kebab-case.ext` for most files
- **Components**: `PascalCase.ext` for React/Vue components
- **Constants**: `UPPER_SNAKE_CASE` for environment variables
- **Directories**: `kebab-case` or `snake_case` consistently

## Security & Best Practices

### Never Commit
- `.env` files with actual secrets
- API keys, passwords, tokens
- Database credentials
- Private certificates

### Always Include
- `.env.example` with placeholder values
- Comprehensive `.gitignore`
- Clear README with setup instructions
- Dependency lock files (`package-lock.json`, `poetry.lock`)

## Configuration Management

1. **Environment-specific configs** in separate files
2. **Secrets** via environment variables only  
3. **Public configs** can be committed
4. **Local overrides** always gitignored

## Documentation Structure

```
docs/
├── README.md              # Getting started
├── API.md                 # API documentation
├── DEPLOYMENT.md          # Deployment guide
├── CONTRIBUTING.md        # Contribution guidelines
└── specs/                 # Technical specifications
```
