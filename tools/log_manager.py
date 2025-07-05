#!/usr/bin/env python3
"""
SysDash Log Manager CLI Tool
Manage encrypted test result logs from the command line
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.test_logger import TestResultLogger
from backend.log_backup import LogBackupManager
from backend.init_logging import cleanup_old_logs

def main():
    parser = argparse.ArgumentParser(description='SysDash Log Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify log file integrity')
    verify_parser.add_argument('--log-file', help='Path to log file')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show log statistics')
    stats_parser.add_argument('--log-file', help='Path to log file')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export logs to new file')
    export_parser.add_argument('output_file', help='Output file path')
    export_parser.add_argument('--password', help='New password for exported file')
    export_parser.add_argument('--log-file', help='Source log file')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create backup of log file')
    backup_parser.add_argument('--log-file', help='Path to log file')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_file', help='Backup file to restore')
    restore_parser.add_argument('--target', help='Target file path')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old log entries')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Days to keep (default: 30)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent test results')
    list_parser.add_argument('--type', help='Filter by test type')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of results to show')
    list_parser.add_argument('--log-file', help='Path to log file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'verify':
            logger = TestResultLogger(args.log_file) if args.log_file else TestResultLogger()
            result = logger.verify_integrity()
            print(f"Status: {result['status']}")
            print(f"Total entries: {result.get('total_entries', 'N/A')}")
            print(f"File size: {result.get('file_size', 'N/A')} bytes")
            if result['status'] == 'corrupted':
                print(f"Corrupted entries: {result.get('corrupted_entries', [])}")
            elif result['status'] == 'error':
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif args.command == 'stats':
            logger = TestResultLogger(args.log_file) if args.log_file else TestResultLogger()
            stats = logger.get_test_statistics()
            print(f"Total tests: {stats['total_tests']}")
            print("Test types:")
            for test_type, count in stats['test_types'].items():
                print(f"  {test_type}: {count}")
            if stats['date_range']:
                print(f"Date range: {stats['date_range']['first']} to {stats['date_range']['last']}")
        
        elif args.command == 'export':
            logger = TestResultLogger(args.log_file) if args.log_file else TestResultLogger()
            success = logger.export_logs(args.output_file, args.password)
            if success:
                print(f"✅ Logs exported to: {args.output_file}")
            else:
                print("❌ Export failed")
        
        elif args.command == 'backup':
            backup_manager = LogBackupManager()
            backup_path = backup_manager.create_backup(args.log_file)
            print(f"✅ Backup created: {backup_path}")
        
        elif args.command == 'restore':
            backup_manager = LogBackupManager()
            success = backup_manager.restore_backup(args.backup_file, args.target)
            if success:
                print(f"✅ Backup restored from: {args.backup_file}")
            else:
                print("❌ Restore failed - integrity check failed")
        
        elif args.command == 'cleanup':
            result = cleanup_old_logs(args.days)
            if 'error' in result:
                print(f"❌ Cleanup failed: {result['error']}")
            else:
                print(f"✅ Cleanup completed:")
                print(f"  Removed: {result['removed_entries']} entries")
                print(f"  Kept: {result['kept_entries']} entries")
                print(f"  Cutoff date: {result['cutoff_date']}")
        
        elif args.command == 'list':
            logger = TestResultLogger(args.log_file) if args.log_file else TestResultLogger()
            
            if args.type:
                if args.type.startswith('benchmark_'):
                    benchmark_type = args.type.replace('benchmark_', '')
                    results = logger.get_benchmark_history(benchmark_type, args.limit)
                elif args.type == 'speedtest':
                    results = logger.get_speedtest_history(args.limit)
                else:
                    results = logger.secure_logger.get_test_results(args.type, args.limit)
            else:
                results = logger.secure_logger.get_test_results(None, args.limit)
            
            print(f"Recent test results ({len(results)} entries):")
            print("-" * 80)
            
            for result in reversed(results[-args.limit:]):  # Show most recent first
                timestamp = result.get('timestamp', 'Unknown')
                test_type = result.get('test_type', 'Unknown')
                test_id = result.get('id', 'N/A')[:8]  # Short ID
                
                print(f"[{timestamp}] {test_type} (ID: {test_id})")
                
                # Show key results
                if 'results' in result:
                    test_results = result['results']
                    if test_type.startswith('benchmark_'):
                        if 'duration_seconds' in test_results:
                            print(f"  Duration: {test_results['duration_seconds']}s")
                        if 'score' in test_results:
                            print(f"  Score: {test_results['score']}")
                        if 'speed_mbps' in test_results:
                            print(f"  Speed: {test_results['speed_mbps']} MB/s")
                    elif test_type == 'speedtest':
                        if 'ping_ms' in test_results:
                            print(f"  Ping: {test_results['ping_ms']} ms")
                        if 'download_speed_mbps' in test_results:
                            print(f"  Download: {test_results['download_speed_mbps']} Mbps")
                        if 'upload_speed_mbps' in test_results:
                            print(f"  Upload: {test_results['upload_speed_mbps']} Mbps")
                
                print()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
