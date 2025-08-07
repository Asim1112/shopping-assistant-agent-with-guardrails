# 🛍️ Shopping Assistant Agent with Input/Output Guardrails

This project is built using the OpenAI Agents SDK with Gemini models.  
It features a smart shopping assistant agent enhanced with input and output guardrails:

- ❌ Blocks illegal product queries (e.g., weapons, drugs)
- ❌ Prevents medical or financial advice in responses
- ✅ Helps users discover products, deals, and shopping tips

## How to Run

1. Clone the repo  
2. Add your `GEMINI_API_KEY` in a `.env` file  
3. Run the script:

```bash
python shopping_agent.py


## Tools & Frameworks
  • OpenAI Agents SDK
  • Gemini 2.5 & 2.0 Models
  • Python Async
  • Pydantic Guardrails