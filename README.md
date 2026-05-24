# SECUREPATCH: Multi-Agent LLM System for Automated Security Vulnerability Repair

[![Paper](https://img.shields.io/badge/Paper-PDF-red)](paper/SECUREPATCH_COMPLETE_PAPER.pdf)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Code Llama](https://img.shields.io/badge/Model-Code_Llama_7B-orange.svg)](https://github.com/facebookresearch/codellama)

> **Achieving 99.4% Success Rate in Automated Security Vulnerability Repair**

SECUREPATCH is a multi-agent Large Language Model (LLM) system that achieves state-of-the-art performance on automated security vulnerability repair. Through specialized agents (Auditor, Architect, Validator, Coordinator) and iterative refinement with automated feedback, SECUREPATCH reaches 99.4% success rate on 160 Python security vulnerabilities across 8 CWE categories.

---

## 🎯 Key Results

- **99.4% Success Rate** (SECUREPATCH-5, 5 iterations)
- **95.6% Success Rate** (SECUREPATCH-3, 3 iterations) - **Production-ready**
- **85.0% Success Rate** (SECUREPATCH-1, single-shot) - Already exceeds all existing approaches
- **+27-88% Improvement** over state-of-the-art methods
- **100% Accuracy** on 7 out of 8 CWE categories
- **First system to cross 95% production reliability threshold**

---

## 🏗️ Architecture

SECUREPATCH employs four specialized agents:

1. **Auditor Agent**: Detects vulnerabilities and generates structured reports with CWE classification
2. **Architect Agent**: Generates secure patches using security-focused prompting
3. **Validator Agent**: Performs syntax validation (Python AST) and security validation (Bandit)
4. **Coordinator Agent**: Orchestrates workflow and manages iterative refinement

![Architecture](paper/figures/Figure11_Architecture.jpg)

### Iterative Refinement

When validation fails, the Coordinator provides specific feedback to the Architect:
- **Syntax errors**: Exact error message and line number
- **Security issues**: Bandit finding details with rule ID
- **Targeted improvement**: Architect refines patch based on feedback

---

## 📊 Performance Comparison

| Approach | Year | Success Rate | Improvement |
|----------|------|--------------|-------------|
| TBar | 2019 | 10.9% | +88.5% |
| Codex | 2021 | 28.8% | +70.6% |
| SequenceR | 2019 | 43.0% | +56.4% |
| ChatGPT (Sobania) | 2023 | 47.5% | +51.9% |
| ChatRepair | 2024 | 48.0% | +51.4% |
| GenProg | 2009 | 55.0% | +44.4% |
| CoCoNut | 2020 | 71.0% | +28.4% |
| ChatGPT (Zhang) | 2023 | 72.0% | +27.4% |
| **SECUREPATCH-1** | **2026** | **85.0%** | **Baseline** |
| **SECUREPATCH-3** | **2026** | **95.6%** | **+10.6%** |
| **SECUREPATCH-5** | **2026** | **99.4%** | **+14.4%** |

---

## 🔧 Installation

### Prerequisites

- Python 3.10 or higher
- Ollama (for local Code Llama deployment)
- Bandit 1.7.5 or higher

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/securepatch.git
cd securepatch

# Install dependencies
pip install -r requirements.txt

# Install Ollama and pull Code Llama 7B
curl -fsSL https://ollama.com/install.sh | sh
ollama pull codellama:7b-instruct

# Install Bandit
pip install bandit==1.7.5
```

---

## 🚀 Quick Start

### Basic Usage

```python
from securepatch import SECUREPATCH

# Initialize system
system = SECUREPATCH(
    model="codellama:7b-instruct",
    max_retries=3,  # SECUREPATCH-3 (recommended)
    temperature=0.1
)

# Repair a vulnerable file
result = system.repair_file("vulnerable_code.py")

print(f"Success: {result.success}")
print(f"Attempts: {result.attempts}")
print(f"Patched code: {result.patched_code}")
```

### Running on Dataset

```bash
# Run experiments on the full dataset
python run_experiments.py --config configs/securepatch_3.yaml

# Run with specific CWE category
python run_experiments.py --cwe CWE-89 --max-retries 3

# Run single file repair
python repair_single.py --input vulnerable.py --output fixed.py --max-retries 5
```

---

## 📁 Dataset

### Composition

Our benchmark contains **160 Python security vulnerabilities** across 8 CWE categories:

| CWE | Vulnerability Type | Count | SECUREPATCH-5 Success |
|-----|-------------------|-------|----------------------|
| CWE-78 | OS Command Injection | 20 | 100% |
| CWE-89 | SQL Injection | 20 | 100% |
| CWE-22 | Path Traversal | 20 | 100% |
| CWE-94 | Code Injection | 20 | 100% |
| CWE-502 | Deserialization | 20 | 100% |
| CWE-798 | Hardcoded Credentials | 20 | 100% |
| CWE-327 | Weak Cryptography | 20 | 95% |
| CWE-918 | SSRF | 20 | 100% |

### Dataset Structure

```
dataset/
├── CWE-78/
│   ├── cmd_injection_01.py
│   ├── cmd_injection_02.py
│   └── ...
├── CWE-89/
│   ├── sql_injection_01.py
│   └── ...
└── metadata.json
```

Each vulnerability includes:
- Vulnerable Python code (10-30 lines)
- Metadata (CWE classification, severity, description)
- Ground truth fix (for validation)

---

## 🔬 Reproduction

### Reproduce Paper Results

```bash
# Run all three configurations
python reproduce_results.py --all

# This will run:
# - SECUREPATCH-1 (1 iteration): ~20s per file, ~53 min total
# - SECUREPATCH-3 (3 iterations): ~23s per file, ~61 min total
# - SECUREPATCH-5 (5 iterations): ~25s per file, ~67 min total

# Results saved to: results/experiment_YYYYMMDD_HHMMSS/
```

### Expected Results

After running the experiments, you should see:

```
SECUREPATCH-1: 85.0% (136/160 successful)
SECUREPATCH-3: 95.6% (152/159 successful) 
SECUREPATCH-5: 99.4% (159/160 successful)
```

---

## 📊 Evaluation Metrics

- **Success Rate**: Percentage of vulnerabilities successfully repaired
- **Average Attempts**: Mean number of patch generation attempts
- **First-Try Success**: Percentage successful on first attempt (79.2% for SECUREPATCH-5)
- **Per-Category Success**: Success rate breakdown by CWE type
- **Marginal Improvement**: Gain from additional iterations
- **Time per File**: Average repair time (20-25 seconds)

### Success Criteria

A repair is successful if and only if:
1. Patched code is syntactically valid (passes Python AST parsing)
2. Patched code has **zero HIGH-severity** Bandit findings
3. Repair achieved within MAX_RETRIES attempts

---

## 🎓 Citation

If you use SECUREPATCH in your research, please cite our paper:

```bibtex
@article{ securepatch,
  title={SECUREPATCH: Specialized Multi-Agent Architecture with Automated Validation for Security Vulnerability Repair},
  author={L.Yashwanth Reddy},
  journal={AVE Trends in Intelligent Computing Systems},
  volume={3},
  number={1},
  pages={23--47},
  year={2026},
  publisher={AVE Trends Publishing Company},
  doi={10.64091/ATICS.2026.000283},
  url={https://www.avepubs.com/user/journals/details/ATICS}
}
```

---

## 📄 Paper

The full paper is available in [`SECUREPATCH.pdf`](SECUREPATCH.pdf).

**Key Sections:**
- Section 3: Multi-Agent Architecture Design
- Section 5: Comprehensive Experimental Results
- Section 6: Failure Mode Analysis & Optimal Strategy Selection

---

## 🛠️ Configuration

### Iteration Strategies

Choose based on your use case:

| Strategy | Success | Overhead | Use Case |
|----------|---------|----------|----------|
| SECUREPATCH-1 | 85.0% | Baseline | Pre-commit CI/CD, fast feedback |
| SECUREPATCH-3 | 95.6% | +15% | **Production systems (recommended)** |
| SECUREPATCH-5 | 99.4% | +25% | Critical systems, maximum reliability |

### Example Configuration

```yaml
# configs/securepatch_3.yaml
model:
  name: "codellama:7b-instruct"
  temperature: 0.1
  max_tokens: 1000

system:
  max_retries: 3
  timeout: 30
  
validator:
  tool: "bandit"
  version: "1.7.5"
  severity_threshold: "HIGH"

logging:
  level: "INFO"
  save_results: true
```

---

## 🐛 Troubleshooting

### Common Issues

**Q: Bandit not detecting vulnerabilities**
```bash
# Verify Bandit installation
bandit --version  # Should be 1.7.5+

# Test on a sample file
bandit -r dataset/CWE-89/sql_injection_01.py
```

**Q: Code Llama not responding**
```bash
# Check Ollama is running
ollama list

# Pull model if missing
ollama pull codellama:7b-instruct

# Test model
ollama run codellama:7b-instruct "def hello():"
```

**Q: Low success rate**
```bash
# Verify temperature setting (should be 0.1)
# Check max_retries matches desired configuration
# Ensure Bandit version is 1.7.5+
```

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Code Llama** by Meta AI for the foundation model
- **Bandit** by PyCQA for security validation
- **OWASP** for security guidelines and CWE classifications
- All baseline approaches that established the foundation for this work

---

## 📧 Contact

- **Author**: L.Yashwanth Reddy
- **Email**: nadhahari44@gmail.com
- **Paper**: [https://www.avepubs.com/user/journals/details/ATICS]
- **Issues**: [GitHub Issues](https://github.com/yourusername/securepatch/issues)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/securepatch&type=Date)](https://star-history.com/#yourusername/securepatch&Date)

---

**Last Updated**: May 2026
