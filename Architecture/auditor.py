from core.llm import query_llm

def audit(code: str) -> str:
    prompt = f"""
You are a Senior Security Auditor.

Analyze this Python code and identify:
- Vulnerability type
- CWE category
- Vulnerable line
- Root cause explanation

Return structured text.

Code:
{code}
"""
    return query_llm(prompt)
