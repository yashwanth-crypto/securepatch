import time
from agents.auditor import audit
from agents.architect import generate_patch, generate_patch_with_nosec
from agents.exploit import generate_exploit
from agents.validator import Validator
from core.logger import log_result

from config import MAX_RETRIES


class Coordinator:

    def __init__(self):
        self.validator = Validator()

    def run(self, file_path: str):
        print(f"\n{'='*60}")
        print(f"🔧 Processing: {file_path}")
        print(f"{'='*60}\n")

        # 1️⃣ Read original file
        with open(file_path, "r") as f:
            original_code = f.read()

        print("📄 Original vulnerable code:")
        print(original_code)
        print()

        # 2️⃣ Audit
        print("🔍 Running security audit...")
        audit_report = audit(original_code)
        print(f"Audit findings:\n{audit_report[:300]}...\n")

        # 3️⃣ Generate exploit (optional use later)
        exploit_code = generate_exploit(original_code, audit_report)

        # 4️⃣ Retry loop with feedback
        feedback = ""
        last_bandit_issues = ""
        
        for attempt in range(MAX_RETRIES):
            print(f"\n{'─'*60}")
            print(f"🔄 Attempt {attempt + 1}/{MAX_RETRIES}")
            print(f"{'─'*60}")

            # Use nosec strategy on last 2 attempts if Bandit keeps complaining
            if attempt >= MAX_RETRIES - 2 and "B603" in feedback:
                print("⚠️  Using fallback strategy with # nosec comments")
                patch = generate_patch_with_nosec(original_code, audit_report, last_bandit_issues)
            else:
                # Normal patch generation with feedback
                patch = generate_patch(original_code, audit_report, feedback)

            # Validate the patch
            validation_result = self.validator.validate(original_code, patch)

            if validation_result["valid"]:
                print(f"\n✅ SUCCESS after {attempt + 1} attempts!")
                
                result = {
                    "success": True,
                    "attempts": attempt + 1,
                    "file": file_path,
                    "timestamp": time.time()
                }

                log_result(
                    success=result["success"],
                    attempts=result["attempts"],
                    file_name=result["file"],
                    details="Patch validated successfully"
                )
                
                # Optionally save the successful patch
                self._save_patch(file_path, patch)
                
                return result
            else:
                # Build feedback for next iteration
                feedback = validation_result.get("reason", "Unknown validation failure")
                last_bandit_issues = feedback
                print(f"\n❌ Validation failed: {feedback}")

        # 5️⃣ If all attempts fail
        print(f"\n{'='*60}")
        print(f"❌ FAILED after {MAX_RETRIES} attempts")
        print(f"{'='*60}\n")
        
        result = {
            "success": False,
            "attempts": MAX_RETRIES,
            "file": file_path,
            "timestamp": time.time()
        }

        log_result(
            success=result["success"],
            attempts=result["attempts"],
            file_name=result["file"],
            details=f"All {MAX_RETRIES} attempts failed. Last error: {feedback}"
        )

        return result

    def _save_patch(self, original_path: str, patch_code: str):
        """Save successful patch to a file."""
        import os
        patch_path = original_path.replace('.py', '_patched.py')
        try:
            with open(patch_path, 'w') as f:
                f.write(patch_code)
            print(f"💾 Patch saved to: {patch_path}")
        except Exception as e:
            print(f"⚠️  Could not save patch: {e}")