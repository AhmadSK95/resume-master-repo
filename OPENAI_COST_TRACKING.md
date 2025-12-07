# OpenAI API Cost Tracking

## Overview

Your Resume Matcher app now tracks OpenAI API usage and costs for every request. Each API response includes detailed token usage and estimated cost in USD.

## Response Format

All endpoints that use OpenAI now return an `api_usage` field:

```json
{
  "api_usage": {
    "prompt_tokens": 450,
    "completion_tokens": 120,
    "total_tokens": 570,
    "cost_usd": 0.0345
  }
}
```

## Pricing (as of Nov 2024)

### GPT-4
- **Prompt tokens**: $0.03 per 1K tokens
- **Completion tokens**: $0.06 per 1K tokens

### GPT-3.5-Turbo
- **Prompt tokens**: $0.0015 per 1K tokens  
- **Completion tokens**: $0.002 per 1K tokens

## Endpoints with Cost Tracking

### 1. **POST /api/analyze-resume**
Analyzes resume and provides improvement suggestions (uses GPT-4)

**Example Response:**
```json
{
  "success": true,
  "filename": "john_doe_resume.pdf",
  "score": 85,
  "analysis": "OVERALL SCORE: 85/100...",
  "api_usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 450,
    "total_tokens": 1650,
    "cost_usd": 0.063
  }
}
```

**Cost breakdown**: `(1200/1000 * 0.03) + (450/1000 * 0.06) = $0.063`

---

### 2. **POST /api/query**
Query resumes with natural language (uses GPT-4)

**Example Request:**
```json
{
  "prompt": "Find senior Python developers with AWS experience",
  "use_openai": true
}
```

**Example Response:**
```json
{
  "prompt": "Find senior Python developers...",
  "analysis": "Based on the resumes provided...",
  "model": "gpt-4",
  "api_usage": {
    "prompt_tokens": 800,
    "completion_tokens": 300,
    "total_tokens": 1100,
    "cost_usd": 0.042
  },
  "top_matches": [...]
}
```

---

### 3. **POST /api/find-references** (with comparison)
Compare user's resume with references (uses GPT-4)

**Example Request:**
```json
{
  "query": "Senior Software Engineer resume",
  "include_comparison": true,
  "user_resume_text": "..."
}
```

**Example Response:**
```json
{
  "query": "Senior Software Engineer...",
  "references": [...],
  "comparison_analysis": "KEY DIFFERENCES: Reference resumes...",
  "api_usage": {
    "prompt_tokens": 950,
    "completion_tokens": 280,
    "total_tokens": 1230,
    "cost_usd": 0.045
  }
}
```

---

### 4. **POST /api/upload** (with OpenAI field extraction)
Extract resume fields using GPT-3.5-Turbo

**Example Request:**
```
POST /api/upload
Content-Type: multipart/form-data

file: resume.pdf
use_openai: true
```

**Example Response:**
```json
{
  "success": true,
  "resume_id": "abc123",
  "fields": {
    "skills": ["Python", "AWS", "Docker"],
    "titles": ["Senior Engineer"],
    "years_exp": 5,
    "api_usage": {
      "prompt_tokens": 320,
      "completion_tokens": 85,
      "total_tokens": 405,
      "cost_usd": 0.00065
    }
  }
}
```

---

## Cost Estimation Examples

### Typical Usage Costs

| Operation | Model | Avg Tokens | Est. Cost |
|-----------|-------|------------|-----------|
| Resume field extraction | GPT-3.5 | 400 | $0.0007 |
| Resume analysis | GPT-4 | 1,500 | $0.06 |
| Query with prompt | GPT-4 | 1,000 | $0.04 |
| Reference comparison | GPT-4 | 1,200 | $0.048 |

### Monthly Cost Estimates

**Light usage** (10 analyses/day):
- 10 resume analyses × 30 days = 300 analyses
- 300 × $0.06 = **~$18/month**

**Medium usage** (50 analyses/day):
- 50 × 30 = 1,500 analyses  
- 1,500 × $0.06 = **~$90/month**

**Heavy usage** (200 analyses/day):
- 200 × 30 = 6,000 analyses
- 6,000 × $0.06 = **~$360/month**

---

## Viewing Costs in Frontend

The frontend automatically receives cost data. You can display it like:

```javascript
// After calling analyzeResume()
const response = await analyzeResume(file);

if (response.api_usage) {
  console.log(`Tokens used: ${response.api_usage.total_tokens}`);
  console.log(`Cost: $${response.api_usage.cost_usd}`);
}
```

## Tracking Total Costs

To track cumulative costs, you can:

1. **Log all requests** to a database with timestamps and costs
2. **Add middleware** to Flask to accumulate costs per session
3. **Use OpenAI dashboard** at https://platform.openai.com/usage for official billing

## Tips to Reduce Costs

1. **Cache results**: Store analysis results to avoid re-analyzing the same resume
2. **Use GPT-3.5 when possible**: 20x cheaper than GPT-4 for simpler tasks
3. **Limit max_tokens**: Reduce `max_tokens` in prompts to cap completion length
4. **Batch operations**: Process multiple items in one API call when feasible
5. **Pre-filter with local models**: Use sentence-transformers first, then OpenAI for top candidates only

## Environment Variables

Make sure to set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
```

Or in `.env` file:
```
OPENAI_API_KEY=sk-...
```

---

## Testing Cost Tracking

Test the API and see costs:

```bash
# Test resume analysis
curl -X POST http://localhost:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find Python developers",
    "use_openai": true
  }'

# Response includes:
# "api_usage": {
#   "total_tokens": 850,
#   "cost_usd": 0.036
# }
```

---

## Need Help?

- **OpenAI Pricing**: https://openai.com/api/pricing/
- **Token Counter**: https://platform.openai.com/tokenizer
- **Usage Dashboard**: https://platform.openai.com/usage
