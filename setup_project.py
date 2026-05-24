#!/usr/bin/env python3
"""
Project Structure Setup
Creates all necessary directories for the research project
"""

import os

def create_project_structure():
    """Create the complete project directory structure"""
    
    directories = [
        "agents",           # Multi-agent components
        "core",            # Core utilities (LLM, logging)
        "dataset",         # Vulnerable code samples
        "dataset/ground_truth",  # Expected fixes
        "results",         # Experiment results
        "figures",         # Generated visualizations
        "logs",            # Detailed logs
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created: {directory}/")
    
    # Create __init__.py files to make them packages
    for directory in ["agents", "core"]:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, 'w').close()
            print(f"✓ Created: {init_file}")
    
    print("\n✅ Project structure created successfully!")

if __name__ == "__main__":
    print("🔧 Setting up project structure...\n")
    create_project_structure()
