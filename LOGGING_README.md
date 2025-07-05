# SysDash Secure Logging System

A comprehensive, encrypted logging system for SysDash that securely stores and manages test results, benchmarks, and system performance data.

## Features

### 🔒 Security
- **AES-256 encryption** for all log data
- **PBKDF2 key derivation** with 100,000 iterations
- **HMAC integrity verification** to detect tampering
- **Secure password handling** with environment variable support
- **Automatic salt generation** for each log file

### 📊 Test Result Management
- **Benchmark logging** for CPU, RAM, disk, and GPU tests
- **Network speed test** result storage
- **Historical data tracking** with timestamps
- **Test statistics** and performance trends
- **Flexible querying** by test type and date range

### 💾 Backup & Recovery
- **Automatic backup creation** with configurable intervals
- **Manual backup management** via API and CLI
- **Backup verification** and integrity checking
- **Point-in-time recovery** from any backup
- **Metadata tracking** for all backups

### 🛠 Management Tools
- **Web interface** for log viewing and management
- **CLI tools** for advanced operations
- **Automatic cleanup** of old entries
- **Log file verification** and repair
- **Export functionality** for data migration

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install cryptography fastapi uvicorn psutil numpy requests

# Run setup script
python setup_logging.py
```

### 2. Configuration

Edit the `.env` file created during setup:

```bash
# Set a secure password
SYSDASH_LOG_PASSWORD=your_secure_password_here

# Configure log file location
SYSDASH_LOG_FILE=logs/test_results.enc

# Set maximum entries to keep
SYSDASH_MAX_LOG_ENTRIES=1000

# Enable automatic backups
SYSDASH_BACKUP_ENABLED=true
SYSDASH_BACKUP_INTERVAL_HOURS=24
```

### 3. Start the Application

```bash
python main.py
```

Visit `http://127.0.0.1:8000/tests` to access the web interface.

## API Endpoints

### Test Execution
- `GET /api/cpu` - Run CPU benchmark
- `GET /api/ram` - Run RAM benchmark  
- `GET /api/disk` - Run disk benchmark
- `GET /api/network` - Run network speed test
- `GET /api/components` - Run full system benchmark

### Log Management
- `GET /api/test-history` - Get test history
- `GET /api/test-statistics` - Get test statistics
- `GET /api/verify-logs` - Verify log integrity
- `POST /api/logs/cleanup` - Clean up old entries

### Backup Management
- `GET /api/logs/backup` - Create backup
- `GET /api/logs/backups` - List backups
- `POST /api/logs/restore` - Restore from backup

## Command Line Tools

### Log Manager CLI

```bash
# Verify log integrity
python tools/log_manager.py verify

# Show statistics
python tools/log_manager.py stats

# List recent tests
python tools/log_manager.py list --limit 20

# Filter by test type
python tools/log_manager.py list --type benchmark_cpu

# Create backup
python tools/log_manager.py backup

# Clean up old entries
python tools/log_manager.py cleanup --days 30

# Export logs
python tools/log_manager.py export exported_logs.enc --password new_password
```

### Test the System

```bash
# Run all tests
python tests/test_logging_system.py
```

## Architecture

### Core Components

1. **SecureLogger** (`backend/crypto_utils.py`)
   - Handles encryption/decryption
   - Manages key derivation
   - Provides integrity verification

2. **TestResultLogger** (`backend/test_logger.py`)
   - High-level logging interface
   - Test result management
   - Historical data queries

3. **LogBackupManager** (`backend/log_backup.py`)
   - Backup creation and restoration
   - Backup metadata management
   - Cleanup operations

4. **Web Interface** (`frontend/tests.html`)
   - Interactive test execution
   - Log viewing and management
   - Real-time statistics

### Data Flow

```
Test Execution → Results → Encryption → Secure Storage
                    ↓
            Backup System ← Log Management ← Web Interface
```

### File Structure

```
logs/
├── test_results.enc          # Main encrypted log file
├── backups/                  # Backup directory
│   ├── test_results_backup_20250101_120000.enc
│   └── test_results_backup_20250101_120000_metadata.json
backend/
├── crypto_utils.py           # Encryption utilities
├── test_logger.py           # Main logging interface
├── log_backup.py            # Backup management
├── init_logging.py          # System initialization
└── logging_config.py        # Configuration management
```

## Security Considerations

### Encryption Details
- **Algorithm**: AES-256 in CBC mode
- **Key Derivation**: PBKDF2 with SHA-256
- **Iterations**: 100,000 (configurable)
- **Salt**: Unique per log file
- **IV**: Random per encryption operation

### Password Management
- Store passwords in environment variables
- Use strong, unique passwords (minimum 12 characters)
- Consider using a password manager
- Rotate passwords periodically

### File Permissions
```bash
# Secure log directory
chmod 700 logs/
chmod 600 logs/*.enc

# Secure backup directory  
chmod 700 logs/backups/
chmod 600 logs/backups/*.enc
```

## Troubleshooting

### Common Issues

**"Could not decrypt log file"**
- Check password in `.env` file
- Verify file hasn't been corrupted
- Try restoring from backup

**"Log file corruption detected"**
- Run integrity verification: `python tools/log_manager.py verify`
- Restore from latest backup
- Check disk space and permissions

**"Backend functions not available"**
- Install missing dependencies
- Check import paths
- Verify Python environment

### Recovery Procedures

**Complete Log Loss**
1. Check backup directory: `logs/backups/`
2. List available backups: `python tools/log_manager.py backup list`
3. Restore latest backup: Use web interface or CLI
4. Verify restored data: `python tools/log_manager.py verify`

**Partial Corruption**
1. Create backup of current state
2. Export uncorrupted entries to new file
3. Replace corrupted file with exported data
4. Verify integrity of new file

## Performance

### Benchmarks
- **Encryption**: ~50MB/s on modern hardware
- **Log Entry**: ~2ms average (including encryption)
- **Backup Creation**: ~100MB/s (file copy speed)
- **Integrity Check**: ~10MB/s (depends on file size)

### Optimization Tips
- Keep log files under 100MB for best performance
- Use automatic cleanup to prevent excessive growth
- Store logs on fast storage (SSD recommended)
- Regular backups prevent large file operations

## Development

### Adding New Test Types

1. **Create test function** in appropriate backend module
2. **Add API endpoint** in `main.py`
3. **Update logging calls** to use `TestResultLogger`
4. **Add UI elements** in `tests.html`

Example:
```python
# In backend/new_test.py
def run_custom_test():
    results = {"metric": 42, "status": "success"}
    return results

# In main.py
@app.get("/api/custom-test")
async def api_custom_test():
    from backend.test_logger import TestResultLogger
    from backend.new_test import run_custom_test
    
    results = run_custom_test()
    
    # Log results
    logger = TestResultLogger()
    logger.log_benchmark_result('custom_test', results)
    
    return results
```

### Extending the Logging System

1. **Custom log fields**: Modify `TestResultLogger.log_benchmark_result()`
2. **New query methods**: Add to `TestResultLogger` class
3. **Additional security**: Enhance `SecureLogger` encryption
4. **Export formats**: Add new export methods

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-logging-feature`
3. Run tests: `python tests/test_logging_system.py`
4. Submit pull request

## License

This logging system is part of SysDash and follows the same license terms.

## Support

For issues and questions:
1. Check this documentation
2. Run the test suite to verify installation
3. Check log files for error messages
4. Create an issue on the project repository

---

**⚠️ Important Security Note**: Always use strong passwords and keep your `.env` file secure. The encrypted logs are only as secure as your password!