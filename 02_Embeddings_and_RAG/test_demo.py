#!/usr/bin/env python3
"""
Demo script showing how to use the RAG application with command line parameters.
This script demonstrates the different ways to test the RAG application.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and display the result."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Demo different ways to test the RAG application."""
    print("🎯 RAG Application Testing Demo")
    print("This demo shows different ways to test your RAG application with PDF support.")
    
    # Check if we're in the right directory
    if not os.path.exists("quick_test.py"):
        print("❌ Please run this script from the project root directory.")
        return False
    
    # Demo 1: Quick test without API key
    print("\n" + "="*80)
    print("📋 DEMO 1: Quick Test (No API Key Required)")
    print("="*80)
    run_command("python quick_test.py", "Testing PDF functionality without API key")
    
    # Demo 2: Quick test with custom PDF
    print("\n" + "="*80)
    print("📋 DEMO 2: Quick Test with Custom PDF")
    print("="*80)
    if os.path.exists("data/ai_research_paper.pdf"):
        run_command("python quick_test.py data/ai_research_paper.pdf", "Testing with specific PDF file")
    else:
        print("⚠️  Sample PDF not found, skipping this demo")
    
    # Demo 3: Comprehensive test
    print("\n" + "="*80)
    print("📋 DEMO 3: Comprehensive Test")
    print("="*80)
    run_command("python test_all.py", "Running comprehensive test suite")
    
    # Demo 4: Show help for each script
    print("\n" + "="*80)
    print("📋 DEMO 4: Command Line Help")
    print("="*80)
    
    scripts = ["quick_test.py", "test_all.py", "test_rag_end_to_end.py"]
    for script in scripts:
        if os.path.exists(script):
            print(f"\n--- Help for {script} ---")
            run_command(f"python {script} --help", f"Help for {script}")
    
    print("\n" + "="*80)
    print("🎉 Demo Complete!")
    print("="*80)
    print("\nTo test with your own PDF and API key:")
    print("1. python quick_test.py your_file.pdf --api-key sk-your-key-here")
    print("2. python test_all.py your_file.pdf --api-key sk-your-key-here")
    print("3. python test_rag_end_to_end.py your_file.pdf --api-key sk-your-key-here")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
