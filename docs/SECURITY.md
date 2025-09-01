# Security Guidelines

- Never commit secrets; use environment variables or secret managers
- In CI, use repository secrets; never echo secrets to logs
- For Firestore, use dedicated staging credentials
- Do not connect to production databases during development/testing

Cross-references:
- Deployment: ./DEPLOYMENT.md

