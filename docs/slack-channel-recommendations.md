# Slack Channel Organization Recommendations

## Overview
Current state: All notifications going to a single channel
Goal: Better visibility for security and critical alerts

## Recommended Channel Structure

### #alerts-critical 🚨
**Purpose:** High-priority alerts requiring immediate attention

**Notification Types:**
- Security alerts (failed logins, unauthorized access attempts)
- Infrastructure failures (Docker containers down on uk-bhr-p-doc-1, vCenter issues)
- Site downtime (jameskilby.co.uk unavailable)
- Deployment failures
- Database issues
- Certificate expiration warnings

**Settings:**
- Notify for all messages
- Enable mobile push notifications
- Star channel for quick access

---

### #deployments
**Purpose:** Track deployment pipeline activity

**Notification Types:**
- GitHub Actions workflows (jkcoukblog repository)
- Cloudflare build completions (jkcoukblog.pages.dev staging)
- WordPress static generation updates
- Successful deployments to jameskilby.co.uk
- Portainer deployment notifications

**Settings:**
- Mentions only (keeps quiet unless attention needed)
- Can be muted during focused work

---

### #monitoring (Optional)
**Purpose:** Routine operational information

**Notification Types:**
- Routine health checks
- Backup completions
- Portainer updates
- Non-critical infrastructure logs
- Mikrotik switch status updates
- vCenter routine notifications

**Settings:**
- Muted (check when needed)
- Review periodically for trends

---

## Implementation Steps

### 1. Create Channels
```
Create three channels in Slack:
- alerts-critical
- deployments
- monitoring (optional)
```

### 2. Configure Notification Settings
- Set #alerts-critical to notify for all messages with mobile push
- Set #deployments to mentions only
- Mute #monitoring

### 3. Set Up Keyword Alerts
Add these keywords to trigger notifications even in non-critical channels:
- "failed"
- "error"
- "critical"
- "security"
- "down"
- "unauthorized"

### 4. Configure Integrations

#### GitHub Actions
- Route to: #deployments (success), #alerts-critical (failures)
- Webhook configuration needed for conditional routing

#### Portainer
- API: ptr_95KAnDFf29UNUF3ue67H0lI10xl1qSo9u8ggF8BOpxw=
- Route container failures to #alerts-critical
- Route routine updates to #monitoring

#### Cloudflare Pages
- Route build completions to #deployments
- Route build failures to #alerts-critical

#### WordPress
- Route static generation completion to #deployments
- Route site errors to #alerts-critical

#### Infrastructure Monitoring
- vCenter alerts to #alerts-critical
- Mikrotik switch alerts to #alerts-critical
- Routine checks to #monitoring

---

## Benefits
- Critical issues never get lost in deployment noise
- Can safely mute non-essential channels during focused work
- Mobile notifications only for what matters
- Historical separation makes troubleshooting easier

---

## Future Considerations
- Add #backups channel if backup notifications become too frequent
- Consider #security-audit for security scan results separate from immediate threats
- Set up weekly digest of #monitoring activity
