"""
Main Experiment Runner
Runs the multi-agent system on the vulnerability dataset
Compatible with original agent code structure
"""

import os
import time
from pathlib import Path
from agents.coordinator import Coordinator


def get_vulnerable_files(dataset_path="dataset"):
    """Get all vulnerable Python files from dataset"""
    files = []
    for f in Path(dataset_path).glob("*.py"):
        # Skip metadata and fixed files
        if not f.name.endswith("_meta.py") and not f.name.endswith("_fixed.py"):
            files.append(str(f))
    return sorted(files)


def run_experiment(dataset_path="dataset"):
    """
    Run the complete experiment on the dataset.
    
    Args:
        dataset_path: Path to dataset directory
    """
    print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                    MULTI-AGENT SECURITY REPAIR SYSTEM                          ║
║                              Experiment Runner                                 ║
╚════════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Load dataset files
    files = get_vulnerable_files(dataset_path)
    
    if not files:
        print(f"❌ No vulnerable files found in {dataset_path}/")
        print("   Run: python create_dataset.py first")
        return
    
    print(f"📊 Dataset Information")
    print(f"{'─'*80}")
    print(f"Dataset Path:      {dataset_path}")
    print(f"Vulnerable Files:  {len(files)}")
    print(f"{'─'*80}\n")
    
    # Initialize coordinator
    coordinator = Coordinator()
    
    # Track statistics
    start_time = time.time()
    results = []
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        print(f"\n{'='*80}")
        print(f"FILE {i}/{len(files)}: {Path(file_path).name}")
        print(f"{'='*80}\n")
        
        try:
            result = coordinator.run(file_path)
            results.append(result)
        except KeyboardInterrupt:
            print("\n\n⚠️  Experiment interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            results.append({
                "file": file_path,
                "success": False,
                "attempts": 0,
                "error": f"Unexpected error: {str(e)}",
                "timestamp": time.time()
            })
    
    # Final summary
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    
    total = len(results)
    successes = sum(1 for r in results if r.get("success"))
    failures = total - successes
    
    print(f"\n📊 Summary Statistics:")
    print(f"{'─'*80}")
    print(f"Total Files Processed:    {total}")
    print(f"Successful Repairs:       {successes} ({successes/total*100:.1f}%)")
    print(f"Failed Repairs:           {failures} ({failures/total*100:.1f}%)")
    
    if successes > 0:
        attempts = [r.get("attempts", 0) for r in results if r.get("success")]
        print(f"Average Attempts:         {sum(attempts)/len(attempts):.2f}")
        print(f"Min/Max Attempts:         {min(attempts)} / {max(attempts)}")
    
    print(f"\nTotal Time:               {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"Average Time per File:    {elapsed/total:.1f}s")
    print(f"{'─'*80}")
    
    print(f"\n📁 Results saved to: results.json")
    
    print("\n📊 Next Step: Run analysis")
    print("   python analyze_results.py")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    dataset_path = "dataset"
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    
    try:
        run_experiment(dataset_path)
    except Exception as e:
        print(f"\n ❌Fatal error: {e}")
        import traceback
        traceback.print_exc()
