# 🤖 AI Interview Bot — Setup Guide

## Step 1 — Groq API Key lo (FREE)
1. console.groq.com pe jao
2. Google se login karo
3. "API Keys" → "Create API Key"
4. Key copy karo (gsk_xxxxx...)

## Step 2 — Key daalo
`app.py` line 7 pe apni key paste karo:
```python
GROQ_API_KEY = "gsk_APNI_KEY_YAHAN"
```

## Step 3 — Run karo
```bash
pip install -r requirements.txt
streamlit run app.py
```

## System Requirements
- RAM: 1-2 GB (4 GB bhi kaam karega easily!)
- Internet connection
- Python 3.8+
- Ollama/GPU bilkul nahi chahiye!
