---
name: email-reply-draft
description: Draft email replies. Use when email needs response, compose reply, follow company tone, write professional responses, auto-reply to clients.
---

# Email Reply Draft Skill

## When to Use
- Email categorized and reply needed
- Client inquiry requires response
- Meeting request needs confirmation
- Information request needs answer
- Follow-up email required

## Input Schema
```json
{
  "original_email": {
    "from": "string",
    "subject": "string",
    "body": "string",
    "received_at": "string"
  },
  "client_info": {
    "name": "string",
    "company": "string",
    "relationship": "string",
    "past_interactions": ["string"]
  },
  "reply_type": "inquiry|confirmation|information|followup|apology",
  "key_points": ["string array - points to address"]
}
```

## Output Schema
```json
{
  "draft_subject": "string",
  "draft_body": "string",
  "tone": "professional|friendly|formal|urgent",
  "word_count": number,
  "contains_links": boolean,
  "hitl_recommended": boolean
}
```

## Company Tone Guidelines

### Default Tone: Professional & Friendly
- Warm but professional greeting
- Clear, concise responses
- Action-oriented closing
- Avoid jargon

### Tone by Context

| Context | Tone |
|---------|------|
| Existing client | Friendly, warm |
| New prospect | Professional, welcoming |
| Complaint/issue | Empathetic, solution-focused |
| Payment discussion | Professional, clear |
| Meeting scheduling | Efficient, flexible |

## Email Structure

### Standard Format
```
Subject: Re: {original_subject}

Dear {Name},

[Opening - acknowledge receipt/context]

[Body - address key points, provide information]

[Call-to-action - next steps if any]

Best regards,
AI Employee
{Your Company}
{Contact Info}
```

### Opening Lines by Context

| Context | Opening |
|---------|---------|
| First contact | "Thank you for reaching out!" |
| Existing client | "Great to hear from you!" |
| Responding to inquiry | "Thanks for your question about..." |
| Following up | "Following up on our previous conversation..." |
| Apology needed | "I apologize for..." |

### Closing Lines

| Context | Closing |
|---------|---------|
| General | "Best regards," |
| Friendly | "Warmly," |
| Action needed | "Looking forward to your response," |
| Meeting scheduled | "See you then," |
| Apology | "Sincerely," |

## Reply Guidelines

### DO
- ✅ Respond within 24 hours (SLA)
- ✅ Address all questions asked
- ✅ Keep under 1000 characters when possible
- ✅ Include clear next steps
- ✅ Proofread before sending
- ✅ Match sender's formality level

### DON'T
- ❌ Use ALL CAPS
- ❌ Send without reviewing (if HITL required)
- ❌ Include unnecessary attachments
- ❌ Make promises without approval
- ❌ Use overly casual language with new contacts

## HITL Recommendation Rules

**Recommend HITL review:**
- First-time contact with sender
- Response involves pricing/quotes
- Response involves commitments/deadlines
- Complaint or sensitive topic
- Legal/contract-related
- Body > 1000 characters
- Contains external links

**Auto-approve (no HITL):**
- Simple confirmation (meeting, receipt)
- Information already approved
- Follow-up to ongoing conversation
- Under 500 characters, known client

## Examples

### Example 1: Client Inquiry (Auto-approve)
**Input:**
```json
{
  "original_email": {
    "from": "john@knownclient.com",
    "subject": "Quick question about timeline",
    "body": "Hi, when can we expect the deliverables?",
    "received_at": "2026-02-17T10:00:00Z"
  },
  "client_info": {
    "name": "John",
    "company": "KnownClient Inc",
    "relationship": "existing",
    "past_interactions": ["Project kickoff Jan 2026"]
  },
  "reply_type": "information",
  "key_points": ["Deliverables due Feb 28", "On track", "Will share update Friday"]
}
```

**Output:**
```json
{
  "draft_subject": "Re: Quick question about timeline",
  "draft_body": "Dear John,\n\nGreat to hear from you! The deliverables are on track for February 28th.\n\nI'll share a detailed progress update this Friday. Everything is moving along as planned.\n\nBest regards,\nAI Employee",
  "tone": "friendly",
  "word_count": 45,
  "contains_links": false,
  "hitl_recommended": false
}
```

### Example 2: New Prospect Pricing Inquiry (HITL Required)
**Input:**
```json
{
  "original_email": {
    "from": "prospect@newcompany.com",
    "subject": "Pricing inquiry",
    "body": "Hi, I'd like to know your pricing for enterprise plan.",
    "received_at": "2026-02-17T09:00:00Z"
  },
  "client_info": {
    "name": "Prospect",
    "company": "New Company",
    "relationship": "new",
    "past_interactions": []
  },
  "reply_type": "inquiry",
  "key_points": ["Enterprise pricing varies", "Need requirements", "Schedule call"]
}
```

**Output:**
```json
{
  "draft_subject": "Re: Pricing inquiry",
  "draft_body": "Dear Prospect,\n\nThank you for your interest in our enterprise plan!\n\nEnterprise pricing is customized based on your specific requirements. To provide an accurate quote, I'd love to learn more about your needs.\n\nWould you be available for a brief call this week? Please let me know what time works best for you.\n\nBest regards,\nAI Employee",
  "tone": "professional",
  "word_count": 65,
  "contains_links": false,
  "hitl_recommended": true
}
```

### Example 3: Meeting Confirmation (Auto-approve)
**Input:**
```json
{
  "original_email": {
    "from": "partner@company.com",
    "subject": "Meeting tomorrow at 2pm?",
    "body": "Can we meet tomorrow at 2pm to discuss the project?",
    "received_at": "2026-02-16T15:00:00Z"
  },
  "client_info": {
    "name": "Partner",
    "company": "Partner Company",
    "relationship": "existing",
    "past_interactions": ["Weekly sync meetings"]
  },
  "reply_type": "confirmation",
  "key_points": ["Confirm 2pm", "Send calendar invite"]
}
```

**Output:**
```json
{
  "draft_subject": "Re: Meeting tomorrow at 2pm?",
  "draft_body": "Dear Partner,\n\nYes, tomorrow at 2pm works perfectly! I'll send over a calendar invite shortly.\n\nLooking forward to our discussion.\n\nWarmly,\nAI Employee",
  "tone": "friendly",
  "word_count": 35,
  "contains_links": false,
  "hitl_recommended": false
}
```

## Related Files
- `Company_Handbook.md` - Company tone and communication guidelines
- `PROCESSING/Pending_Approval/` - Where drafts awaiting approval are stored
- `KNOWLEDGE/Contexts/clients.md` - Client information for personalization
