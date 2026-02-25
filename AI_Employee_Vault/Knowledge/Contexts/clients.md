# Clients Database

**Version:** 1.0  
**Last Updated:** 2026-02-17  
**Location:** `KNOWLEDGE/Contexts/clients.md`

---

## How to Add a Client

```markdown
### Client Name
- **Email:** name@company.com
- **Company:** Company Name
- **Relationship:** existing|prospect|vendor
- **Started:** YYYY-MM-DD
- **Notes:** Any relevant notes
- **Autonomy:** auto_approve|hitl_required
```

---

## Active Clients

*No clients added yet. Add your first client above.*

---

## Prospects

*No prospects added yet.*

---

## Vendors

*No vendors added yet.*

---

## Domain Trust List

Trusted domains (all emails from these domains are auto_approve):

- `@yourcompany.com` - Internal team

---

## Past Interactions Log

See `SYSTEM/state/task_history.jsonl` for complete interaction history.

---

## Notes

- This file is used by the `client-lookup` Qwen skill
- Update when new client onboarded
- Mark inactive clients in a separate section
- Never delete client records (archive instead)
