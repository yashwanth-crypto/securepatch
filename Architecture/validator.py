import ast
import json
import os
import tempfile
import subprocess

from config import TIMEOUT


class Validator:

    def __init__(self, bandit_config_path=".bandit"):
        """
        Initialize validator.
        
        Args:
            bandit_config_path: Path to .bandit config file (optional)
        """
        self.bandit_config = bandit_config_path if os.path.exists(bandit_config_path) else None

    def syntax_check(self, code: str) -> tuple[bool, str]:
        """Check Python syntax. Returns (is_valid, error_message)"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"

    def run_bandit(self, file_path: str) -> tuple[int, str]:
        """
        Run Bandit security scanner. Returns (issue_count, details)
        
        Uses custom config if available to reduce false positives.
        """
        try:
            cmd = ["python", "-m", "bandit", file_path, "-f", "json"]
            
            # Add config file if it exists
            if self.bandit_config:
                cmd.extend(["-c", self.bandit_config])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

            # Handle empty output
            if not result.stdout or result.stdout.strip() == "":
                return 999, "Bandit returned empty output"

            # Try to parse JSON
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                return 999, f"Bandit JSON parse error: {str(e)}\nOutput: {result.stdout[:200]}"

            results = data.get("results", [])
            
            # Filter to only HIGH severity issues
            high_severity = [r for r in results if r.get("issue_severity") == "HIGH"]
            issue_count = len(high_severity)
            
            # Build detailed report
            if issue_count > 0:
                details = f"{issue_count} HIGH severity issues found:\n"
                for r in high_severity[:3]:  # Show first 3 issues
                    details += f"  - {r.get('test_id', 'N/A')}: {r.get('issue_text', 'N/A')} (Line {r.get('line_number', 'N/A')})\n"
                return issue_count, details
            else:
                # Show info about filtered issues
                total_issues = len(results)
                if total_issues > 0:
                    return 0, f"No HIGH severity issues (filtered {total_issues} LOW/MEDIUM warnings)"
                else:
                    return 0, "No security issues detected ✓"

        except subprocess.TimeoutExpired:
            return 999, f"Bandit timed out after {TIMEOUT} seconds"
        except FileNotFoundError:
            return 999, "Bandit not installed. Run: pip install bandit"
        except Exception as e:
            return 999, f"Bandit execution error: {str(e)}"

    def validate(self, original_code: str, patched_code: str) -> dict:
        """
        Validate patched code.
        
        Returns:
            dict with keys:
                - valid (bool): Whether patch is valid
                - reason (str): Explanation if invalid
        """

        print("\n" + "="*60)
        print("PATCH VALIDATION")
        print("="*60)
        print(patched_code[:500])  # Show first 500 chars
        if len(patched_code) > 500:
            print(f"... ({len(patched_code) - 500} more characters)")
        print("="*60 + "\n")

        # 1. Syntax check
        is_valid_syntax, syntax_error = self.syntax_check(patched_code)
        if not is_valid_syntax:
            print("❌ Syntax check failed")
            return {
                "valid": False,
                "reason": f"Syntax error: {syntax_error}"
            }
        else:
            print("✅ Syntax check passed")

        # 2. Write to temp file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp:
                tmp.write(patched_code)
                tmp_path = tmp.name
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Failed to write temp file: {str(e)}"
            }

        # 3. Run bandit
        issues, details = self.run_bandit(tmp_path)
        print(f"🔍 Bandit scan: {details}")

        # 4. Cleanup
        try:
            os.remove(tmp_path)
        except Exception:
            pass  # Best effort cleanup

        # 5. Determine validity
        if issues == 0:
            print("✅ All security checks passed!")
            return {
                "valid": True,
                "reason": "All checks passed"
            }
        elif issues == 999:
            return {
                "valid": False,
                "reason": f"Validation error: {details}"
            }
        else:
            return {
                "valid": False,
                "reason": f"Security issues remain: {details}"
            }