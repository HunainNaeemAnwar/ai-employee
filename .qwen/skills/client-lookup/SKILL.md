---
name: client-lookup
description: Check if sender is known client. Use when processing emails, verify sender identity, retrieve client history, look up contact information, determine relationship status.
---

# Client Lookup Skill

## When to Use
- New email received, need to identify sender
- Before drafting reply, check client history
- Determine if HITL required based on sender status
- Look up client contact information
- Check relationship status with sender

## Input Schema
```json
{
  "email_address": "string (sender's email)",
  "domain": "string (optional, extracted from email)",
  "subject": "string (optional, for context)"
}
```

## Output Schema
```json
{
  "is_known_client": boolean,
  "client_name": "string or null",
  "company": "string or null",
  "relationship": "existing|new|prospect|vendor|unknown",
  "email_domain_match": boolean,
  "past_interactions": ["string array"],
  "notes": "string",
  "autonomy_level": "auto_approve|hitl_required"
}
```

## Lookup Process

### Step 1: Check clients.md
Search `Knowledge/Contexts/clients.md` for:
- Exact email match
- Domain match (e.g., @company.com)
- Name match

### Step 2: Check Past Interactions
Search in:
- `Done/` - Previous completed tasks
- `.system/state/task_history.jsonl` - Historical records
- Email thread history

### Step 3: Determine Relationship

| Match Type | Relationship |
|------------|--------------|
| Email in clients.md | "existing" |
| Domain in clients.md | "existing" |
| Name in clients.md (different email) | "prospect" |
| No match found | "new" |

### Step 4: Determine Autonomy Level

**auto_approve:**
- Relationship = "existing"
- No previous issues/complaints
- Standard request type

**hitl_required:**
- Relationship = "new" (first contact)
- Relationship = "prospect"
- Previous issues noted
- Sensitive request (payment, legal)

## clients.md Format

Expected format in `Knowledge/Contexts/clients.md`:

```markdown
# Clients Database

## Active Clients

### Client Name
- **Email:** name@company.com
- **Company:** Company Name
- **Relationship:** existing
- **Started:** 2025-01-15
- **Notes:** Long-term client, weekly projects
- **Autonomy:** auto_approve

### Another Client
- **Email:** contact@another.com
- **Domain:** @another.com (all emails from this domain trusted)
- **Company:** Another Corp
- **Relationship:** existing
- **Notes:** Enterprise client
- **Autonomy:** auto_approve

## Prospects

### Prospect Name
- **Email:** prospect@newco.com
- **Company:** NewCo
- **Relationship:** prospect
- **Notes:** Interested in enterprise plan
- **Autonomy:** hitl_required

## Vendors

### Vendor Name
- **Email:** billing@vendor.com
- **Company:** Vendor Inc
- **Relationship:** vendor
- **Notes:** Monthly invoices
- **Autonomy:** hitl_required (payment-related)
```

## Decision Rules

### Known Client Indicators
- ✔ Email exactly matches entry in clients.md
- ✔ Email domain matches trusted domain in clients.md
- ✔ Name matches and email is slight variation (typo, different address)
- ✔ Previous completed tasks from same email

### New Contact Indicators
- ✖ No email match
- ✖ No domain match
- ✖ No name match
- ✖ First interaction ever recorded

### Red Flags (Always HITL)
- 🚩 Email similar to known client but different domain (potential spoofing)
- 🚩 Free email provider (gmail.com, yahoo.com) claiming to be business
- 🚩 Previous fraud/spam noted
- 🚩 Requesting sensitive actions (payment, data access)

## Examples

### Example 1: Known Client Lookup
**Input:**
```json
{
  "email_address": "john@acmecorp.com",
  "domain": "acmecorp.com",
  "subject": "Project update needed"
}
```

**Lookup Result in clients.md:**
```markdown
### John Smith
- **Email:** john@acmecorp.com
- **Company:** Acme Corp
- **Relationship:** existing
- **Autonomy:** auto_approve
```

**Output:**
```json
{
  "is_known_client": true,
  "client_name": "John Smith",
  "company": "Acme Corp",
  "relationship": "existing",
  "email_domain_match": true,
  "past_interactions": [
    "Project kickoff 2026-01-15",
    "Weekly sync 2026-02-01",
    "Deliverable review 2026-02-10"
  ],
  "notes": "Long-term client, auto_approve enabled",
  "autonomy_level": "auto_approve"
}
```

### Example 2: New Contact Lookup
**Input:**
```json
{
  "email_address": "stranger@unknown.com",
  "domain": "unknown.com",
  "subject": "Business inquiry"
}
```

**Lookup Result:** No match in clients.md

**Output:**
```json
{
  "is_known_client": false,
  "client_name": null,
  "company": null,
  "relationship": "new",
  "email_domain_match": false,
  "past_interactions": [],
  "notes": "First contact - HITL required per policy",
  "autonomy_level": "hitl_required"
}
```

### Example 3: Domain Match Lookup
**Input:**
```json
{
  "email_address": "sarah@trustedclient.com",
  "domain": "trustedclient.com",
  "subject": "Urgent request"
}
```

**Lookup Result in clients.md:**
```markdown
### Trusted Client Corp
- **Domain:** @trustedclient.com (all emails trusted)
- **Company:** Trusted Client Corp
- **Relationship:** existing
- **Autonomy:** auto_approve
```

**Output:**
```json
{
  "is_known_client": true,
  "client_name": "Trusted Client Corp",
  "company": "Trusted Client Corp",
  "relationship": "existing",
  "email_domain_match": true,
  "past_interactions": [
    "Enterprise contract 2025-06-01",
    "Multiple projects completed"
  ],
  "notes": "All @trustedclient.com emails are auto_approve",
  "autonomy_level": "auto_approve"
}
```

### Example 4: Prospect Lookup
**Input:**
```json
{
  "email_address": "prospect@newcompany.com",
  "domain": "newcompany.com",
  "subject": "Pricing question"
}
```

**Lookup Result in clients.md:**
```markdown
### New Company Prospect
- **Email:** prospect@newcompany.com
- **Company:** New Company
- **Relationship:** prospect
- **Notes:** Inquired via website, interested in pricing
- **Autonomy:** hitl_required
```

**Output:**
```json
{
  "is_known_client": true,
  "client_name": "New Company Prospect",
  "company": "New Company",
  "relationship": "prospect",
  "email_domain_match": true,
  "past_interactions": [
    "Website inquiry 2026-02-15"
  ],
  "notes": "Prospect - pricing inquiries require HITL",
  "autonomy_level": "hitl_required"
}
```

## Related Files
- `Knowledge/Contexts/clients.md` - Client database
- `.system/state/task_history.jsonl` - Interaction history
- `Done/` - Past completed tasks
- `email-triage` skill - Uses client lookup for categorization
- `email-reply-draft` skill - Uses client info for personalization
