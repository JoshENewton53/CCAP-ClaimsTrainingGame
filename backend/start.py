#!/usr/bin/env python3
"""
Startup verification script for CCAP Claims Training Game backend
"""
import sys
import os

def check_dependencies():
    """Check if all required dependencies are available"""
    print("Checking dependencies...")
    
    required_modules = [
        'flask',
        'flask_cors',
        'pandas',
        'numpy',
        'transformers',
        'torch',
        'sklearn',
        'reportlab'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        return False
    
    print("\n✓ All dependencies installed")
    return True

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    
    required_dirs = [
        'reference_data',
        '../ai_models',
        '../ai_models/models'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ⚠ {dir_path} - NOT FOUND (will be created if needed)")
    
    return True

def check_files():
    """Check if required files exist"""
    print("\nChecking files...")
    
    required_files = [
        'reference_data/code_mappings.json',
        'app.py',
        'ai_service.py'
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        return False
    
    print("\n✓ All required files present")
    return True

def main():
    """Run all checks"""
    print("=" * 60)
    print("CCAP Claims Training Game - Startup Verification")
    print("=" * 60)
    
    checks = [
        check_dependencies(),
        check_directories(),
        check_files()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All checks passed - starting application...")
        print("=" * 60 + "\n")
        
        # Import and run the app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Some checks failed - please fix the issues above")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
