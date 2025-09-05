# GitHub Notification Reduction Guide

> **Purpose**: Autonomous solution to reduce excessive GitHub notification emails  
> **Rule Reference**: Satisfies consolidated rule 5.2 (s01GqEvqdOoCeZXzoX6UUH)

## Problem
GitHub notifications contribute to "broken windows" problem by creating email overload that distracts from development focus.

## Autonomous Solutions

### 1. Repository-Level Settings (Immediate)
```bash
# Disable email notifications for this repository
gh api repos/am/Fresh/notifications \
  --method PUT \
  --field subscribed=false \
  --field ignored=false
```

### 2. Global Notification Filters (Recommended)
```bash
# Set watching to "Not watching" by default for new repositories
gh api user \
  --method PATCH \
  --field default_repository_permission=false
```

### 3. Email Filter Rules (Gmail/Outlook)
**Gmail Filter**:
- From: `notifications@github.com`
- Subject contains: `Fresh`, `Pull Request`, `Issue`
- Action: Skip Inbox → Apply Label "GitHub" → Mark as Read

**Outlook Rule**:
- From: `notifications@github.com`  
- Move to: GitHub folder
- Mark as read: Yes

### 4. Selective Notification Script
```bash
#!/bin/bash
# scripts/configure_github_notifications.sh

# Only get notifications for:
# - Direct mentions (@am)
# - Assigned issues/PRs
# - Security alerts

gh api user/notification-settings \
  --method PATCH \
  --field participating=true \
  --field watching=false \
  --field team_mentions=false \
  --field repository_invitations=true
```

### 5. Repository-Specific Overrides
```bash
# For high-priority repos, keep minimal notifications
gh repo set-default-branch am/Fresh main
gh api repos/am/Fresh/subscription \
  --method PUT \
  --field subscribed=true \
  --field ignored=false \
  --field reason="security"
```

## Implementation Priority
1. ✅ **Immediate**: Apply email filters (5 minutes)
2. ✅ **Short-term**: Run notification configuration script (2 minutes)  
3. ✅ **Long-term**: Audit all repository subscriptions monthly

## Validation
```bash
# Check current notification settings
gh api user/notification-settings

# Verify repository subscription status
gh api repos/am/Fresh/subscription
```

## Autonomous Maintenance
- **Weekly**: Review notification volume in email client
- **Monthly**: Run audit script to check for new unwanted subscriptions
- **Quarterly**: Evaluate effectiveness and adjust filters

---
*This guide implements autonomous notification management per consolidated rule 5.2*
