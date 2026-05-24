"""
Results Analysis
Analyzes experimental results
Compatible with original logger format
"""

import json
import os
from pathlib import Path
from collections import defaultdict


def load_results(results_file="results.json"):
    """Load results from JSON file"""
    
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        return []
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    return results if isinstance(results, list) else []


def load_dataset_metadata(dataset_path="dataset"):
    """Load dataset metadata"""
    metadata_file = os.path.join(dataset_path, "dataset_metadata.json")
    
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return None


def analyze_overall_performance(results):
    """Compute overall performance metrics"""
    if not results:
        return None
    
    total = len(results)
    successes = sum(1 for r in results if r.get("success"))
    failures = total - successes
    
    # Attempt statistics
    all_attempts = [r.get("attempts", 0) for r in results]
    success_attempts = [r.get("attempts", 0) for r in results if r.get("success")]
    
    metrics = {
        "total_files": total,
        "successes": successes,
        "failures": failures,
        "success_rate": (successes / total * 100) if total > 0 else 0,
        "mean_attempts": (sum(all_attempts) / len(all_attempts)) if all_attempts else 0,
        "mean_attempts_success": (sum(success_attempts) / len(success_attempts)) if success_attempts else 0,
        "min_attempts": min(success_attempts) if success_attempts else 0,
        "max_attempts": max(success_attempts) if success_attempts else 0,
    }
    
    return metrics


def analyze_by_vulnerability(results, metadata):
    """Analyze results by vulnerability type (CWE)"""
    
    # Group by CWE (extract from filename pattern)
    cwe_stats = defaultdict(lambda: {"total": 0, "success": 0, "attempts": []})
    
    # Mapping from filename prefixes to CWE IDs
    cwe_mapping = {
        "cmd_injection": "CWE-78",
        "sql_injection": "CWE-89",
        "path_traversal": "CWE-22",
        "code_injection": "CWE-94",
        "deserialization": "CWE-502",
        "hardcoded_creds": "CWE-798",
        "weak_crypto": "CWE-327",
        "ssrf": "CWE-918",
    }
    
    for result in results:
        filename = Path(result["file"]).stem
        
        # Find CWE from filename
        cwe_id = None
        for key, value in cwe_mapping.items():
            if filename.startswith(key):
                cwe_id = value
                break
        
        if cwe_id:
            cwe_stats[cwe_id]["total"] += 1
            if result.get("success"):
                cwe_stats[cwe_id]["success"] += 1
                cwe_stats[cwe_id]["attempts"].append(result.get("attempts", 0))
    
    # Calculate rates
    for cwe_id in cwe_stats:
        total = cwe_stats[cwe_id]["total"]
        success = cwe_stats[cwe_id]["success"]
        cwe_stats[cwe_id]["success_rate"] = (success / total * 100) if total > 0 else 0
        
        attempts = cwe_stats[cwe_id]["attempts"]
        cwe_stats[cwe_id]["avg_attempts"] = (sum(attempts) / len(attempts)) if attempts else 0
        
        # Add name from metadata
        if metadata and cwe_id in metadata.get("vulnerabilities", {}):
            cwe_stats[cwe_id]["name"] = metadata["vulnerabilities"][cwe_id]["name"]
            cwe_stats[cwe_id]["severity"] = metadata["vulnerabilities"][cwe_id]["severity"]
    
    return dict(cwe_stats)


def print_report(results):
    """Print comprehensive analysis report"""
    
    print("\n" + "="*80)
    print("RESULTS ANALYSIS REPORT")
    print("="*80 + "\n")
    
    if not results:
        print("❌ No results to analyze")
        return
    
    # Overall performance
    overall = analyze_overall_performance(results)
    
    print("📊 OVERALL PERFORMANCE")
    print("─"*80)
    print(f"Total Files:              {overall['total_files']}")
    print(f"Successful Repairs:       {overall['successes']} ({overall['success_rate']:.1f}%)")
    print(f"Failed Repairs:           {overall['failures']}")
    print(f"Mean Attempts (All):      {overall['mean_attempts']:.2f}")
    print(f"Mean Attempts (Success):  {overall['mean_attempts_success']:.2f}")
    print(f"Attempt Range:            {overall['min_attempts']}-{overall['max_attempts']}")
    print()
    
    # By vulnerability type
    metadata = load_dataset_metadata()
    cwe_stats = analyze_by_vulnerability(results, metadata)
    
    if cwe_stats:
        print("🔍 PERFORMANCE BY VULNERABILITY TYPE")
        print("─"*80)
        print(f"{'CWE':<12} {'Type':<35} {'Success Rate':<15} {'Avg Attempts'}")
        print("─"*80)
        
        for cwe_id in sorted(cwe_stats.keys()):
            stats = cwe_stats[cwe_id]
            name = stats.get("name", "Unknown")[:33]
            success_rate = stats["success_rate"]
            avg_attempts = stats["avg_attempts"]
            
            print(f"{cwe_id:<12} {name:<35} {success_rate:>6.1f}%         {avg_attempts:>4.2f}")
        
        print()
    
    # Failed cases
    failed = [r for r in results if not r.get("success")]
    if failed:
        print("❌ FAILED CASES")
        print("─"*80)
        for r in failed[:10]:  # Show first 10
            filename = Path(r["file"]).name
            error = r.get("error", "Unknown error")[:60]
            print(f"  • {filename}: {error}")
        
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")
        print()
    
    # Success stories
    successes = [r for r in results if r.get("success")]
    if successes:
        first_try = [r for r in successes if r.get("attempts") == 1]
        print("✅ SUCCESS HIGHLIGHTS")
        print("─"*80)
        print(f"First-Try Successes:      {len(first_try)}/{len(successes)} ({len(first_try)/len(successes)*100:.1f}%)")
        print()
    
    print("="*80 + "\n")


def generate_latex_table(results):
    """Generate LaTeX table for research paper"""
    
    overall = analyze_overall_performance(results)
    metadata = load_dataset_metadata()
    cwe_stats = analyze_by_vulnerability(results, metadata)
    
    print("\n📄 LaTeX Table (copy to your paper):\n")
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\caption{Performance by Vulnerability Type}")
    print("\\label{tab:results}")
    print("\\begin{tabular}{llrrr}")
    print("\\hline")
    print("\\textbf{CWE} & \\textbf{Vulnerability} & \\textbf{Total} & \\textbf{Success Rate} & \\textbf{Avg Attempts} \\\\")
    print("\\hline")
    
    if cwe_stats:
        for cwe_id in sorted(cwe_stats.keys()):
            stats = cwe_stats[cwe_id]
            name = stats.get("name", "Unknown").replace("&", "\\&")
            total = stats["total"]
            success_rate = stats["success_rate"]
            avg_attempts = stats["avg_attempts"]
            
            print(f"{cwe_id} & {name} & {total} & {success_rate:.1f}\\% & {avg_attempts:.2f} \\\\")
    
    print("\\hline")
    print(f"\\textbf{{Overall}} & & {overall['total_files']} & {overall['success_rate']:.1f}\\% & {overall['mean_attempts_success']:.2f} \\\\")
    print("\\hline")
    print("\\end{tabular}")
    print("\\end{table}\n")


if __name__ == "__main__":
    import sys
    
    # Load results
    results_file = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    results = load_results(results_file)
    
    if not results:
        print("No results to analyze. Run experiments first:")
        print("  python run_experiments.py")
    else:
        print_report(results)
        
        # Optional: Generate LaTeX table
        response = input("\nGenerate LaTeX table for paper? (y/n): ")
        if response.lower() == 'y':
            generate_latex_table(results)
