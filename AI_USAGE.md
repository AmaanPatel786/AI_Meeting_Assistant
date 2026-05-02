# 🧠 AI Usage Report

This document tracks how AI was used during development, including prompts, outputs, fixes, and learnings.

It shows iteration, debugging decisions, and how raw AI output was shaped into a reliable backend system.

---

## 📌 Example 1

### Prompt
"Summarize meeting notes and extract action items with owners and priority"

### AI Output
- Generated structured summary
- Included action items with owners
- Formatting was inconsistent across runs

### What I changed
- Tightened prompt structure in backend
- Forced explicit JSON schema output format
- Removed free-text flexibility in instructions

### Why
The model sometimes adds extra natural language text, which breaks API parsing.

### What I learned
Prompt constraints directly control output stability more than model choice.

---

## 📌 Example 2

### Prompt
"Return ONLY JSON output with summary and action items"

### AI Output
- Sometimes valid JSON
- Sometimes partial JSON or markdown wrapped output
- Occasional extra explanation text

### What I changed
- Added JSON parsing + exception handling in Python
- Implemented fallback response structure
- Sanitized raw response before parsing

### Why
LLMs are probabilistic and not guaranteed to return strict schemas.

### What I learned
Never rely on raw LLM output in production systems without validation.

---

## 📌 Example 3

### Prompt
"Generate fallback summary if AI fails"

### AI Output
- Basic summary fallback logic
- Simple extraction from raw text
- Minimal intelligence in edge cases

### What I changed
- Improved keyword detection (bug, delay, issue, slow, crash)
- Added default owner assignment logic
- Ensured system always returns usable output

### Why
API failures or malformed responses must not break UX.

### What I learned
Fallback systems are not optional — they are core architecture.

---

## 📌 Example 4 (Bonus Insight)

### Prompt
"Make output more human readable"

### AI Output
- Verbose responses
- Inconsistent formatting across runs
- UI-unfriendly structure

### What I changed
- Enforced summary length limits
- Standardized UI rendering format
- Separated AI output from frontend formatting logic

### Why
AI output should serve UI consumption, not just generation.

### What I learned
Good AI apps are UI-aware systems, not just prompt engines.

---

## 🧠 Final Takeaway

- Prompt engineering is iterative, not one-shot
- Backend validation is essential for reliability
- Fallback logic ensures production stability
- Structured outputs are more important than verbose intelligence
- AI must be constrained to become useful in real systems