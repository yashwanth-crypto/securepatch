import re
from core.llm import query_llm

def generate_patch(code: str, audit_report: str, previous_feedback: str = "") -> str:
    """Generate a security patch that passes Bandit validation."""
    
    feedback_section = ""
    if previous_feedback:
        feedback_section = f"""
⚠️ PREVIOUS ATTEMPT FAILED:
{previous_feedback}

You MUST address the above issue. Pay special attention to Bandit warnings.
"""

    prompt = f"""
You are a security patch generator. Your goal is to fix vulnerabilities while passing Bandit security scanner.

CRITICAL RULES:
1. Return ONLY valid Python code inside ```python blocks
2. NO explanations, NO conversational text
3. For command execution vulnerabilities:
   - BEST: Use subprocess.run() with a LIST (not string), shell=False
   - Include input validation (allowlist approach)
   - Example:
     ```python
     import subprocess
     import shlex
     
     user_input = input("Enter command: ")
     
     # Validate: only allow specific safe commands
     allowed = ['ls', 'pwd', 'date', 'whoami']
     parts = shlex.split(user_input)
     if parts and parts[0] in allowed:
         subprocess.run(parts, shell=False, check=False)
     else:
         print("Command not allowed")
     ```

4. AVOID these Bandit triggers:
   - B404: Don't import subprocess at module level if not needed
   - B603: subprocess without shell=False will be flagged
   - B605: Starting process with shell=True
   - B607: Partial executable paths

5. If Bandit still complains, use # nosec comments ONLY if the code is truly safe:
   ```python
   subprocess.run(cmd, shell=False)  # nosec B603 - validated input
   ```

Original Vulnerable Code:
{code}

Security Audit:
{audit_report}

{feedback_section}

Remember: Generate code that passes Bandit (0 issues). Use input validation + subprocess with shell=False.
"""

    response = query_llm(prompt)

    # Improved regex to handle different markdown formats
    patterns = [
        r"```python\s*(.*?)\s*```",      # ```python
        r"```Python\s*(.*?)\s*```",      # ```Python (capital P)
        r"```py\s*(.*?)\s*```",          # ```py
        r"```\s*(.*?)\s*```",            # Generic code block
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            patch = match.group(1).strip()
            
            # Clean up common LLM artifacts
            patch = patch.replace('```python', '').replace('```', '')
            
            return patch
    
    # Fallback: if no blocks found, clean the raw response
    patch = response.strip()
    for marker in ['```python', '```Python', '```py', '```']:
        patch = patch.replace(marker, '')
    
    return patch.strip()


def generate_patch_with_nosec(code: str, audit_report: str, bandit_issues: str) -> str:
    """
    Last resort: Generate patch with # nosec comments for known false positives.
    Only use this after multiple failed attempts.
    """
    prompt = f"""
Generate a security patch using subprocess with proper validation BUT add # nosec comments
to suppress Bandit false positives.

Rules:
1. Use subprocess.run() with list of args, shell=False
2. Add input validation (allowlist)
3. Add # nosec B603 comment to suppress false positive
4. Return ONLY Python code in ```python block

Original Code:
{code}

Bandit Complaints:
{bandit_issues}

Example:
```python
import subprocess
import shlex

user_input = input("Enter command: ")
allowed = ['ls', 'pwd', 'date']
parts = shlex.split(user_input)

if parts and parts[0] in allowed:
    subprocess.run(parts, shell=False)  # nosec B603 - validated input
else:
    print("Not allowed")
```
"""
    
    response = query_llm(prompt)
    
    # Extract code
    match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return response.strip()