#!/usr/bin/env python3
"""
SysDash Logging System Setup Script
Initializes the secure logging system with all necessary components
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'cryptography',
        'fastapi',
        'uvicorn',
        'psutil',
        'numpy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required dependencies are installed")
    return True

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        'logs',
        'logs/backups',
        'backend',
        'frontend',
        'static',
        'tests',
        'tools'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_logging_system():
    """Initialize the logging system"""
    try:
        from backend.init_logging import initialize_logging
        logger = initialize_logging()
        print("✅ Logging system initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize logging system: {e}")
        return False

def run_tests():
    """Run the logging system tests"""
    try:
        from tests.test_logging_system import run_all_tests
        success = run_all_tests()
        if success:
            print("✅ All tests passed")
        else:
            print("⚠️ Some tests failed")
        return success
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def create_sample_env():
    """Create a sample .env file"""
    env_content = """# SysDash Configuration
SYSDASH_LOG_FILE=logs/test_results.enc
SYSDASH_LOG_PASSWORD=change_this_password
SYSDASH_MAX_LOG_ENTRIES=1000
SYSDASH_BACKUP_ENABLED=true
SYSDASH_BACKUP_INTERVAL_HOURS=24
SYSDASH_HOST=127.0.0.1
SYSDASH_PORT=8000
SYSDASH_DEBUG=false
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env configuration file")
        print("⚠️ Please edit .env and change the default password!")
    else:
        print("ℹ️ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 SysDash Logging System Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directory_structure()
    
    # Create sample environment file
    create_sample_env()
    
    # Initialize logging system
    if not initialize_logging_system():
        print("❌ Setup failed during logging system initialization")
        sys.exit(1)
    
    # Run tests
    print("\n🧪 Running system tests...")
    if not run_tests():
        print("⚠️ Setup completed but some tests failed")
        print("The system should still work, but please check the logs")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and set a secure password")
    print("2. Run: python main.py")
    print("3. Open http://127.0.0.1:8000/tests in your browser")
    print("\nFor command-line log management:")
    print("python tools/log_manager.py --help")

if __name__ == '__main__':
    main()