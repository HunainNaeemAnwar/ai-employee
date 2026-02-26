---
name: ceo-briefing-generator
description: Generate weekly CEO briefing report every Monday 7 AM. Use when creating executive summary, weekly audit, business metrics report, task completion summary, or CEO dashboard.
---

# CEO Briefing Generator Skill

## When to Use
- Scheduled: Every Monday 7 AM (automated)
- On-demand: User requests weekly report or CEO briefing
- End of week: Generate summary for stakeholders

## Input Schema
```json
{
  "week_start": "ISO 8601 date (Monday)",
  "week_end": "ISO 8601 date (Sunday)",
  "vault_path": "string - path to AI_Employee_Vault"
}
```

## Output Schema
```json
{
  "report_path": "string - path to generated report",
  "summary": {
    "total_tasks": number,
    "completed_tasks": number,
    "pending_tasks": number,
    "hitl_actions": number,
    "emails_processed": number
  },
  "report_content": "string - full markdown report"
}
```

## Report Structure

### 1. Executive Summary
```markdown
# CEO Weekly Briefing
**Week:** {week_start} to {week_end}
**Generated:** {timestamp}

## ✔ Key Metrics

| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Tasks Completed | X | 100+ | ✔/⚠️ |
| Emails Processed | X | 200+ | ✔/⚠️ |
| Auto-Approve Rate | X% | 60% | ✔/⚠️ |
| HITL Actions | X | - | ℹ️ |
| Avg Response Time | X min | <30 min | ✔/⚠️ |
```

### 2. Task Breakdown
```markdown
## ✔ Task Breakdown

### By Type
| Type | Count | % of Total |
|------|-------|------------|
| Email Replies | X | X% |
| Invoices Generated | X | X% |
| Meeting Scheduled | X | X% |
| Data Entry | X | X% |

### By Priority
| Priority | Count | Completed | Pending |
|----------|-------|-----------|---------|
| High | X | X | X |
| Medium | X | X | X |
| Low | X | X | X |
```

### 3. Top Wins
```markdown
## ✔ Top Wins This Week

1. **Largest Task Completed:** {task_name} - {impact}
2. **Fastest Response:** {task_name} - {time} minutes
3. **Most Complex:** {task_name} - {details}
4. **Cost Savings:** {amount} saved via {action}
```

### 4. Pending Items Requiring Attention
```markdown
## ⚠️ Pending Items Requiring CEO Attention

| Item | Age | Priority | Action Needed |
|------|-----|----------|---------------|
| {task} | X days | High | Approval/Decision |
```

### 5. System Health
```markdown
## ✔ System Health

| Component | Status | Uptime | Issues |
|-----------|--------|--------|--------|
| Gmail Watcher | ✔ Active | 99.9% | None |
| Ralph Loop | ✔ Active | 100% | None |
| Email MCP | ✔ Active | 99.5% | None |
```

### 6. Recommendations
```markdown
## ✔ Recommendations for Next Week

1. **Priority Focus:** {recommendation based on pending high-priority tasks}
2. **Process Improvement:** {suggestion based on bottlenecks}
3. **Cost Optimization:** {identified savings opportunity}
```

## Data Sources

### Scan These Folders
| Folder | Purpose |
|--------|---------|
| `Done/` | Completed tasks this week |
| `Reports/` | Previous reports (for comparison) |
| `Logs/` | Action logs for metrics |
| `.system/state/task_history.jsonl` | Full task history |

### Calculate Metrics
```python
# Pseudo-code for metric calculation
total_tasks = count_files("Done/", pattern="*.json")
emails_processed = count_lines_matching("Logs/*.jsonl", "email_sent")
hitl_actions = count_lines_matching("Logs/*.jsonl", "hitl: true")
auto_approve_rate = (total_tasks - hitl_actions) / total_tasks * 100
```

## Generation Process

### Step 1: Collect Data
1. Scan `Done/` for tasks completed this week
2. Parse `.system/state/task_history.jsonl` for all task records
3. Aggregate `Logs/*.jsonl` for action counts

### Step 2: Calculate Metrics
1. Total tasks completed
2. Emails processed and sent
3. HITL approval rate
4. Average response time
5. Task completion by type and priority

### Step 3: Generate Report
1. Create markdown file: `Reports/ceo_briefing_{week_end}.md`
2. Fill in all sections with calculated data
3. Add comparison to previous week (if available)
4. Highlight anomalies and recommendations

### Step 4: Save and Notify
1. Save report to `Reports/`
2. Update `Dashboard.md` with summary metrics
3. Log generation to audit trail
4. (Optional) Email report to CEO

## Examples

### Example 1: First Week Report
**Input:**
```json
{
  "week_start": "2026-02-16",
  "week_end": "2026-02-22",
  "vault_path": "/home/hunain/personal_assistant/AI_Employee_Vault"
}
```

**Output:**
```markdown
# CEO Weekly Briefing
**Week:** 2026-02-16 to 2026-02-22
**Generated:** 2026-02-22 07:00:00

## ✔ Key Metrics

| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Tasks Completed | 47 | 100+ | ⚠️ 47% |
| Emails Processed | 89 | 200+ | ⚠️ 44% |
| Auto-Approve Rate | 62% | 60% | ✔ |
| HITL Actions | 17 | - | ℹ️ |
| Avg Response Time | 12 min | <30 min | ✔ |

## ✔ Task Breakdown

### By Type
| Type | Count | % of Total |
|------|-------|------------|
| Email Replies | 35 | 74% |
| Invoices Generated | 5 | 11% |
| Meeting Scheduled | 4 | 9% |
| Data Entry | 3 | 6% |

## ✔ Top Wins This Week

1. **Largest Task Completed:** Invoice batch processing - Generated 5 invoices in 2 minutes
2. **Fastest Response:** Urgent client email - 3 minutes
3. **Most Complex:** Contract review with 15 attachments - 45 minutes
4. **Cost Savings:** $0 (first week - baseline established)

## ⚠️ Pending Items Requiring CEO Attention

| Item | Age | Priority | Action Needed |
|------|-----|----------|---------------|
| Vendor contract approval | 2 days | High | Review and approve |

## ✔ Recommendations for Next Week

1. **Priority Focus:** Clear pending approval queue (1 high-priority item)
2. **Process Improvement:** Consider auto-approving known vendor invoices
3. **Cost Optimization:** Review subscription costs for potential savings
```

### Example 2: Mature System (Week 8)
**Input:**
```json
{
  "week_start": "2026-04-06",
  "week_end": "2026-04-12",
  "vault_path": "/home/hunain/personal_assistant/AI_Employee_Vault"
}
```

**Output:**
```markdown
# CEO Weekly Briefing
**Week:** 2026-04-06 to 2026-04-12
**Generated:** 2026-04-12 07:00:00

## ✔ Key Metrics

| Metric | This Week | Last Week | Target | Status |
|--------|-----------|-----------|--------|--------|
| Tasks Completed | 156 | 142 | 100+ | ✔ +10% |
| Emails Processed | 312 | 289 | 200+ | ✔ +8% |
| Auto-Approve Rate | 71% | 68% | 60% | ✔ |
| HITL Actions | 45 | 46 | - | ℹ️ |
| Avg Response Time | 8 min | 11 min | <30 min | ✔ |

## ✔ Top Wins This Week

1. **Largest Task Completed:** Q1 financial reconciliation - Processed 500 transactions
2. **Cost Savings:** $847/month identified (unused subscriptions)
3. **Revenue Generated:** $12,500 (auto-generated invoices)

## ✔ Recommendations for Next Week

1. **Cost Optimization:** Cancel 3 unused subscriptions (save $847/month = $10,164/year)
2. **Process Improvement:** Auto-approve invoices under $100 from known vendors
3. **Priority Focus:** Review Q2 budget proposals
```

## Related Files
- `Done/` - Completed task archive
- `Reports/` - Historical reports
- `Logs/` - Action audit trail
- `.system/state/task_history.jsonl` - Task history
- `Dashboard.md` - Real-time status (update with summary)

## Scheduling

### Cron Expression (Monday 7 AM)
```
0 7 * * 1
```

### Manual Invocation
```bash
qwen --file AI_Employee_Vault/.system/state/prompt.md --prompt "Generate CEO briefing for this week"
```
