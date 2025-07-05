import json
import base64
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class SecureLogger:
    def __init__(self, password: str = None, log_file: str = "test_results.enc"):
        self.log_file = log_file
        self.password = password or self._generate_default_password()
        self.key = self._derive_key(self.password)
        self.fernet = Fernet(self.key)
        
    def _generate_default_password(self) -> str:
        """Generate a default password based on system info"""
        import platform
        import getpass
        
        # Create a unique password based on system characteristics
        system_info = f"{platform.node()}-{platform.system()}-{getpass.getuser()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:32]
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        # Use a fixed salt for consistency (in production, use random salt stored separately)
        salt = b'sysdash_salt_2025'  # 16 bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _calculate_checksum(self, data: dict) -> str:
        """Calculate checksum for data integrity"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _load_encrypted_data(self) -> list:
        """Load and decrypt existing log data"""
        if not os.path.exists(self.log_file):
            return []
        
        try:
            with open(self.log_file, 'rb') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return []
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
            
            # Verify data integrity
            if not self._verify_data_integrity(data):
                raise ValueError("Data integrity check failed - possible tampering detected")
            
            return data.get('results', [])
            
        except Exception as e:
            print(f"Error loading encrypted data: {e}")
            return []
    
    def _save_encrypted_data(self, data: list):
        """Encrypt and save log data"""
        try:
            # Create data structure with metadata
            log_data = {
                'version': '1.0.0',
                'created': datetime.now().isoformat(),
                'results': data,
                'checksum': self._calculate_checksum({'results': data})
            }
            
            # Encrypt data
            json_data = json.dumps(log_data, indent=2)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            # Write to file
            with open(self.log_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            print(f"Error saving encrypted data: {e}")
    
    def _verify_data_integrity(self, data: dict) -> bool:
        """Verify data integrity using checksum"""
        if 'checksum' not in data or 'results' not in data:
            return False
        
        expected_checksum = self._calculate_checksum({'results': data['results']})
        return data['checksum'] == expected_checksum
    
    def log_test_result(self, test_type: str, results: dict, metadata: dict = None):
        """Log a test result securely"""
        # Load existing data
        existing_data = self._load_encrypted_data()
        
        # Create new log entry
        log_entry = {
            'id': hashlib.md5(f"{datetime.now().isoformat()}-{test_type}".encode()).hexdigest(),
            'timestamp': datetime.now().isoformat(),
            'test_type': test_type,
            'results': results,
            'metadata': metadata or {},
            'system_info': self._get_system_snapshot(),
            'integrity_hash': self._calculate_checksum(results)
        }
        
        # Add to existing data
        existing_data.append(log_entry)
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(existing_data) > 1000:
            existing_data = existing_data[-1000:]
        
        # Save encrypted data
        self._save_encrypted_data(existing_data)
        
        return log_entry['id']
    
    def get_test_results(self, test_type: str = None, limit: int = None) -> list:
        """Retrieve test results"""
        data = self._load_encrypted_data()
        
        if test_type:
            data = [entry for entry in data if entry['test_type'] == test_type]
        
        if limit:
            data = data[-limit:]
        
        return data
    
    def get_statistics(self) -> dict:
        """Get statistics about logged tests"""
        data = self._load_encrypted_data()
        
        if not data:
            return {'total_tests': 0, 'test_types': {}, 'date_range': None}
        
        test_types = {}
        dates = []
        
        for entry in data:
            test_type = entry['test_type']
            test_types[test_type] = test_types.get(test_type, 0) + 1
            dates.append(entry['timestamp'])
        
        return {
            'total_tests': len(data),
            'test_types': test_types,
            'date_range': {
                'first': min(dates),
                'last': max(dates)
            } if dates else None
        }
    
    def _get_system_snapshot(self) -> dict:
        """Get basic system info for context"""
        import platform
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            memory_total = psutil.virtual_memory().total
        except:
            cpu_count = None
            memory_total = None
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'cpu_count': cpu_count,
            'memory_total': memory_total,
            'python_version': platform.python_version()
        }
    
    def export_results(self, output_file: str, password: str = None) -> bool:
        """Export results to a new encrypted file"""
        if password and password != self.password:
            # Create new logger with different password
            new_logger = SecureLogger(password, output_file)
            data = self._load_encrypted_data()
            new_logger._save_encrypted_data(data)
            return True
        else:
            # Copy current file
            import shutil
            shutil.copy2(self.log_file, output_file)
            return True
    
    def verify_file_integrity(self) -> dict:
        """Verify the integrity of the log file"""
        try:
            data = self._load_encrypted_data()
            
            # Check each entry's integrity
            corrupted_entries = []
            for i, entry in enumerate(data):
                if 'integrity_hash' in entry and 'results' in entry:
                    expected_hash = self._calculate_checksum(entry['results'])
                    if entry['integrity_hash'] != expected_hash:
                        corrupted_entries.append(i)
            
            return {
                'status': 'valid' if not corrupted_entries else 'corrupted',
                'total_entries': len(data),
                'corrupted_entries': corrupted_entries,
                'file_exists': os.path.exists(self.log_file),
                'file_size': os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'file_exists': os.path.exists(self.log_file)
            }