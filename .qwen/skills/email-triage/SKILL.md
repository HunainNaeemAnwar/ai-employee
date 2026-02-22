---
name: email-triage
description: Categorize and prioritize emails from Gmail. Use when new email arrives, process inbox, detect urgent messages, identify invoices, classify incoming emails.
---

# Email Triage Skill

## When to Use
- New email detected in `INPUT_QUEUES/Gmail/`
- Need to categorize incoming email
- Need to calculate priority level
- Need to determine if HITL approval required

## Input Schema
```json
{
  "from": "string (email address)",
  "subject": "string",
  "body": "string",
  "labels": ["string array"],
  "received_at": "ISO 8601 timestamp"
}
```

## Output Schema
```json
{
  "category": "urgent|invoice|promotional|general",
  "priority": "high|medium|low",
  "hitl_required": boolean,
  "reasoning": "string"
}
```

## Categorization Rules

### Category Detection

**invoice** (any match):
- subject or body contains: "invoice", "payment", "bill", "receipt", "billing", "paid", "amount due"

**urgent** (any match):
- subject or body contains: "urgent", "asap", "deadline", "important", "priority", "emergency", "eod", "today"
- Gmail label includes: "IMPORTANT" or "STARRED"

**promotional** (any match):
- Gmail label includes: "CATEGORY_PROMOTIONS"
- Body contains: "unsubscribe", "opt-out", "marketing", "newsletter"
- Body contains external marketing links

**general**:
- Everything else (default)

## Priority Calculation

**Score-based system:**

| Factor | Score |
|--------|-------|
| Known client (in clients.md) | +30 |
| "urgent" keyword | +20 |
| "asap" keyword | +20 |
| "invoice/payment" keyword | +15 |
| "deadline" keyword | +15 |
| Gmail "IMPORTANT" label | +20 |
| Gmail "STARRED" label | +15 |
| Unknown sender | +10 |

**Priority thresholds:**
- **high**: score >= 50
- **medium**: score >= 25
- **low**: score < 25

## HITL Required Rules

**Always require HITL (human approval):**
- Unknown sender (not in clients.md)
- Email body > 1000 characters
- Contains external links (http:// or https://)
- Payment/invoice related (category = "invoice")
- Contains attachments

**Auto-approve (no HITL):**
- Known client AND body < 1000 chars AND no external links AND category != "invoice"

## Examples

### Example 1: Urgent Client Email (Auto-approve)
**Input:**
```json
{
  "from": "john@knownclient.com",
  "subject": "URGENT: Contract Review Needed",
  "body": "Hi, need your review on attached contract by EOD. Please confirm receipt.",
  "labels": ["IMPORTANT", "INBOX"]
}
```

**Output:**
```json
{
  "category": "urgent",
  "priority": "high",
  "hitl_required": false,
  "reasoning": "Known client with urgent keywords, but standard request under 1000 chars"
}
```

### Example 2: Unknown Sender with Link (HITL Required)
**Input:**
```json
{
  "from": "stranger@example.com",
  "subject": "Check this out!",
  "body": "Hey, see this link: http://suspicious.com/deal",
  "labels": ["INBOX"]
}
```

**Output:**
```json
{
  "category": "general",
  "priority": "medium",
  "hitl_required": true,
  "reasoning": "Unknown sender + contains external link"
}
```

### Example 3: Invoice from Vendor (HITL Required)
**Input:**
```json
{
  "from": "billing@vendor.com",
  "subject": "Invoice #12345 - Payment Due",
  "body": "Please find attached invoice for services rendered. Amount due: $5000.",
  "labels": ["INBOX"]
}
```

**Output:**
```json
{
  "category": "invoice",
  "priority": "high",
  "hitl_required": true,
  "reasoning": "Invoice/payment related - always requires HITL per policy"
}
```

### Example 4: Promotional Email (Auto-archive)
**Input:**
```json
{
  "from": "newsletter@marketing.com",
  "subject": "50% Off Sale - Today Only!",
  "body": "Don't miss out! Click here to unsubscribe.",
  "labels": ["CATEGORY_PROMOTIONS"]
}
```

**Output:**
```json
{
  "category": "promotional",
  "priority": "low",
  "hitl_required": false,
  "reasoning": "Promotional email - can auto-archive"
}
```

## Related Files
- `INPUT_QUEUES/Gmail/` - Where new email action files are dropped
- `PROCESSING/Pending/` - Where categorized tasks are queued
- `KNOWLEDGE/Contexts/clients.md` - Known client list for lookup
