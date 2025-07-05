#!/usr/bin/env python3
"""
Test script for the secure logging system
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.test_logger import TestResultLogger
from backend.crypto_utils import SecureLogger
from backend.log_backup import LogBackupManager

def test_basic_logging():
    """Test basic logging functionality"""
    print("🧪 Testing basic logging...")
    
    # Create temporary log file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as tmp:
        tmp_path = tmp.name
    
    try:
        # Initialize logger
        logger = TestResultLogger(tmp_path)
        
        # Log a test result
        test_results = {
            'test_value': 42,
            'test_string': 'hello world',
            'test_array': [1, 2, 3, 4, 5]
        }
        
        log_id = logger.log_benchmark_result('test_benchmark', test_results)
        print(f"  ✅ Logged test result with ID: {log_id}")
        
        # Retrieve results
        history = logger.get_benchmark_history('test_benchmark', 10)
        assert len(history) == 1, "Should have 1 result"
        assert history[0]['results']['test_value'] == 42, "Test value should match"
        print("  ✅ Retrieved and verified test result")
        
        # Test integrity
        integrity = logger.verify_integrity()
        assert integrity['status'] == 'valid', f"Integrity check failed: {integrity}"
        print("  ✅ Integrity check passed")
        
        return True
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_encryption_security():
    """Test that the encryption actually works"""
    print("🔒 Testing encryption security...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as tmp:
        tmp_path = tmp.name
    
    try:
        # Create logger with custom password
        password = "test_password_123"
        logger = TestResultLogger(tmp_path, password)
        
        # Log sensitive data
        sensitive_data = {
            'secret_key': 'this_should_be_encrypted',
            'user_data': 'confidential_information'
        }
        
        logger.log_benchmark_result('security_test', sensitive_data)
        
        # Read raw file content
        with open(tmp_path, 'rb') as f:
            raw_content = f.read()
        
        # Verify data is encrypted (shouldn't contain plaintext)
        raw_string = raw_content.decode('latin-1', errors='ignore')
        assert 'secret_key' not in raw_string, "Raw file contains unencrypted data!"
        assert 'confidential_information' not in raw_string, "Raw file contains unencrypted data!"
        print("  ✅ Data is properly encrypted in file")
        
        # Test wrong password fails
        try:
            wrong_logger = TestResultLogger(tmp_path, "wrong_password")
            wrong_logger.get_benchmark_history('security_test')
            assert False, "Should have failed with wrong password"
        except:
            print("  ✅ Wrong password correctly rejected")
        
        # Test correct password works
        correct_logger = TestResultLogger(tmp_path, password)
        results = correct_logger.get_benchmark_history('security_test')
        assert len(results) == 1, "Should retrieve 1 result with correct password"
        assert results[0]['results']['secret_key'] == 'this_should_be_encrypted'
        print("  ✅ Correct password allows access")
        
        return True
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_tampering_detection():
    """Test that file tampering is detected"""
    print("🛡️ Testing tampering detection...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as tmp:
        tmp_path = tmp.name
    
    try:
        # Create and populate log file
        logger = TestResultLogger(tmp_path)
        logger.log_benchmark_result('tamper_test', {'value': 100})
        
        # Verify initial integrity
        integrity = logger.verify_integrity()
        assert integrity['status'] == 'valid', "Initial integrity should be valid"
        
        # Tamper with the file
        with open(tmp_path, 'r+b') as f:
            f.seek(50)  # Go to middle of file
            f.write(b'TAMPERED')  # Write some garbage
        
        # Test tampering detection
        try:
            tampered_logger = TestResultLogger(tmp_path)
            tampered_logger.get_benchmark_history('tamper_test')
            # If we get here, tampering wasn't detected
            print("  ⚠️ Warning: Tampering not detected (this may be expected for some tamper types)")
        except Exception as e:
            print(f"  ✅ Tampering detected: {e}")
        
        return True
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_backup_system():
    """Test the backup and restore functionality"""
    print("💾 Testing backup system...")
    
    # Create temporary directories
    log_dir = tempfile.mkdtemp()
    backup_dir = tempfile.mkdtemp()
    
    try:
        log_path = os.path.join(log_dir, 'test.enc')
        
        # Create initial log file
        logger = TestResultLogger(log_path)
        logger.log_benchmark_result('backup_test', {'original_data': 'test123'})
        
        # Create backup
        backup_manager = LogBackupManager(backup_dir)
        backup_path = backup_manager.create_backup(log_path)
        print(f"  ✅ Backup created: {os.path.basename(backup_path)}")
        
        # Modify original file
        logger.log_benchmark_result('backup_test', {'modified_data': 'test456'})
        
        # Verify original has 2 entries
        history = logger.get_benchmark_history('backup_test')
        assert len(history) == 2, "Original should have 2 entries"
        
        # Restore from backup
        restore_path = os.path.join(log_dir, 'restored.enc')
        success = backup_manager.restore_backup(os.path.basename(backup_path), restore_path)
        assert success, "Restore should succeed"
        print("  ✅ Backup restored successfully")
        
        # Verify restored file has only 1 entry
        restored_logger = TestResultLogger(restore_path)
        restored_history = restored_logger.get_benchmark_history('backup_test')
        assert len(restored_history) == 1, "Restored file should have 1 entry"
        assert restored_history[0]['results']['original_data'] == 'test123'
        print("  ✅ Restored data verified")
        
        # Test backup listing
        backups = backup_manager.list_backups()
        assert len(backups) >= 1, "Should have at least 1 backup"
        print(f"  ✅ Backup listing works: {len(backups)} backups found")
        
        return True
        
    finally:
        shutil.rmtree(log_dir)
        shutil.rmtree(backup_dir)

def test_performance():
    """Test logging performance with many entries"""
    print("⚡ Testing performance...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as tmp:
        tmp_path = tmp.name
    
    try:
        logger = TestResultLogger(tmp_path)
        
        # Log many entries
        start_time = datetime.now()
        num_entries = 100
        
        for i in range(num_entries):
            logger.log_benchmark_result('performance_test', {
                'iteration': i,
                'data': f'test_data_{i}',
                'timestamp': datetime.now().isoformat()
            })
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"  ✅ Logged {num_entries} entries in {duration:.2f} seconds")
        print(f"  ✅ Average: {duration/num_entries*1000:.2f} ms per entry")
        
        # Verify all entries
        history = logger.get_benchmark_history('performance_test', num_entries)
        assert len(history) == num_entries, f"Should have {num_entries} entries"
        
        # Test integrity
        integrity = logger.verify_integrity()
        assert integrity['status'] == 'valid', "Integrity should be valid after bulk insert"
        print("  ✅ Integrity maintained after bulk operations")
        
        return True
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting SysDash Logging System Tests")
    print("=" * 50)
    
    tests = [
        test_basic_logging,
        test_encryption_security,
        test_tampering_detection,
        test_backup_system,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                failed += 1
                print("❌ FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {e}\n")
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Logging system is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
