#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Logging Infrastructure for Website Monitoring
網站監控增強日誌基礎設施

This module provides comprehensive logging capabilities for the website monitoring system,
including structured logging, performance metrics, and log management.
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import threading
import time


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured logging with JSON output
    """
    
    def __init__(self, include_extra: bool = True):
        """
        Initialize structured formatter
        
        Args:
            include_extra: Whether to include extra fields in log records
        """
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON
        
        Args:
            record: Log record to format
            
        Returns:
            str: Formatted log message
        """
        # Base log structure
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if enabled
        if self.include_extra and hasattr(record, '__dict__'):
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    extra_fields[key] = value
            
            if extra_fields:
                log_entry['extra'] = extra_fields
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class MonitoringLogger:
    """
    Enhanced logging system for website monitoring
    
    Provides:
    - Structured logging with JSON format
    - Performance metrics logging
    - Log rotation and management
    - Multiple output handlers
    - Real-time log monitoring
    """
    
    def __init__(self, name: str = "website_monitoring", log_dir: str = "logs"):
        """
        Initialize monitoring logger
        
        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different log types
        self.performance_log_dir = self.log_dir / "performance"
        self.error_log_dir = self.log_dir / "errors"
        self.audit_log_dir = self.log_dir / "audit"
        
        for log_subdir in [self.performance_log_dir, self.error_log_dir, self.audit_log_dir]:
            log_subdir.mkdir(exist_ok=True)
        
        # Initialize loggers
        self.main_logger = None
        self.performance_logger = None
        self.error_logger = None
        self.audit_logger = None
        
        # Performance tracking
        self.performance_metrics = {}
        self.metrics_lock = threading.Lock()
        
        # Setup logging
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup all logger instances with appropriate handlers"""
        
        # Main application logger
        self.main_logger = logging.getLogger(f"{self.name}.main")
        self.main_logger.setLevel(logging.INFO)
        self._setup_main_logger_handlers()
        
        # Performance metrics logger
        self.performance_logger = logging.getLogger(f"{self.name}.performance")
        self.performance_logger.setLevel(logging.INFO)
        self._setup_performance_logger_handlers()
        
        # Error logger
        self.error_logger = logging.getLogger(f"{self.name}.errors")
        self.error_logger.setLevel(logging.WARNING)
        self._setup_error_logger_handlers()
        
        # Audit logger
        self.audit_logger = logging.getLogger(f"{self.name}.audit")
        self.audit_logger.setLevel(logging.INFO)
        self._setup_audit_logger_handlers()
        
        # Prevent propagation to root logger
        for logger in [self.main_logger, self.performance_logger, self.error_logger, self.audit_logger]:
            logger.propagate = False
    
    def _setup_main_logger_handlers(self):
        """Setup handlers for main application logger"""
        
        # File handler with rotation
        main_log_file = self.log_dir / f"{self.name}_main.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(StructuredFormatter())
        self.main_logger.addHandler(file_handler)
        
        # Daily rotating file handler
        daily_handler = logging.handlers.TimedRotatingFileHandler(
            self.log_dir / f"{self.name}_daily.log",
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        daily_handler.setFormatter(StructuredFormatter())
        self.main_logger.addHandler(daily_handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        self.main_logger.addHandler(console_handler)
    
    def _setup_performance_logger_handlers(self):
        """Setup handlers for performance metrics logger"""
        
        # Performance metrics file
        perf_log_file = self.performance_log_dir / f"{self.name}_performance.log"
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        perf_handler.setFormatter(StructuredFormatter())
        self.performance_logger.addHandler(perf_handler)
        
        # Daily performance summary
        perf_daily_handler = logging.handlers.TimedRotatingFileHandler(
            self.performance_log_dir / f"{self.name}_performance_daily.log",
            when='midnight',
            interval=1,
            backupCount=90,  # Keep 90 days of performance data
            encoding='utf-8'
        )
        perf_daily_handler.setFormatter(StructuredFormatter())
        self.performance_logger.addHandler(perf_daily_handler)
    
    def _setup_error_logger_handlers(self):
        """Setup handlers for error logger"""
        
        # Error log file
        error_log_file = self.error_log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setFormatter(StructuredFormatter())
        self.error_logger.addHandler(error_handler)
        
        # Critical errors to separate file
        critical_handler = logging.FileHandler(
            self.error_log_dir / f"{self.name}_critical.log",
            encoding='utf-8'
        )
        critical_handler.setLevel(logging.CRITICAL)
        critical_handler.setFormatter(StructuredFormatter())
        self.error_logger.addHandler(critical_handler)
    
    def _setup_audit_logger_handlers(self):
        """Setup handlers for audit logger"""
        
        # Audit log file (never rotated for compliance)
        audit_log_file = self.audit_log_dir / f"{self.name}_audit.log"
        audit_handler = logging.FileHandler(
            audit_log_file,
            encoding='utf-8'
        )
        audit_handler.setFormatter(StructuredFormatter())
        self.audit_logger.addHandler(audit_handler)
        
        # Daily audit files for easier management
        audit_daily_handler = logging.handlers.TimedRotatingFileHandler(
            self.audit_log_dir / f"{self.name}_audit_daily.log",
            when='midnight',
            interval=1,
            backupCount=365,  # Keep 1 year of audit logs
            encoding='utf-8'
        )
        audit_daily_handler.setFormatter(StructuredFormatter())
        self.audit_logger.addHandler(audit_daily_handler)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with optional extra fields"""
        self.main_logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with optional extra fields"""
        self.main_logger.warning(message, extra=kwargs)
        self.error_logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message with optional extra fields"""
        self.main_logger.error(message, extra=kwargs)
        self.error_logger.error(message, extra=kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """Log critical message with optional extra fields"""
        self.main_logger.critical(message, extra=kwargs)
        self.error_logger.critical(message, extra=kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """
        Log performance metrics
        
        Args:
            operation: Operation name
            duration: Operation duration in seconds
            **kwargs: Additional performance data
        """
        perf_data = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        self.performance_logger.info(f"Performance: {operation}", extra=perf_data)
        
        # Update performance metrics
        with self.metrics_lock:
            if operation not in self.performance_metrics:
                self.performance_metrics[operation] = {
                    'count': 0,
                    'total_duration': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0,
                    'last_execution': None
                }
            
            metrics = self.performance_metrics[operation]
            metrics['count'] += 1
            metrics['total_duration'] += duration
            metrics['min_duration'] = min(metrics['min_duration'], duration)
            metrics['max_duration'] = max(metrics['max_duration'], duration)
            metrics['last_execution'] = datetime.now().isoformat()
    
    def log_audit(self, action: str, user: str = "system", **kwargs):
        """
        Log audit event
        
        Args:
            action: Action performed
            user: User who performed the action
            **kwargs: Additional audit data
        """
        audit_data = {
            'action': action,
            'user': user,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        self.audit_logger.info(f"Audit: {action}", extra=audit_data)
    
    def start_operation(self, operation: str) -> 'OperationTimer':
        """
        Start timing an operation
        
        Args:
            operation: Operation name
            
        Returns:
            OperationTimer: Timer context manager
        """
        return OperationTimer(self, operation)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance metrics summary
        
        Returns:
            Dict: Performance summary
        """
        with self.metrics_lock:
            summary = {}
            
            for operation, metrics in self.performance_metrics.items():
                if metrics['count'] > 0:
                    avg_duration = metrics['total_duration'] / metrics['count']
                    
                    summary[operation] = {
                        'count': metrics['count'],
                        'average_duration': avg_duration,
                        'min_duration': metrics['min_duration'],
                        'max_duration': metrics['max_duration'],
                        'total_duration': metrics['total_duration'],
                        'last_execution': metrics['last_execution']
                    }
            
            return summary
    
    def log_system_health(self, health_data: Dict[str, Any]):
        """
        Log system health metrics
        
        Args:
            health_data: System health information
        """
        health_info = {
            'health_check': True,
            'timestamp': datetime.now().isoformat(),
            **health_data
        }
        
        self.performance_logger.info("System Health Check", extra=health_info)
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files
        
        Args:
            days_to_keep: Number of days to keep logs
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for log_dir in [self.log_dir, self.performance_log_dir, self.error_log_dir]:
                for log_file in log_dir.glob("*.log*"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        self.log_info(f"Cleaned up old log file: {log_file}")
            
            self.log_audit("log_cleanup", days_kept=days_to_keep)
            
        except Exception as e:
            self.log_error(f"Error cleaning up logs: {e}")


class OperationTimer:
    """
    Context manager for timing operations
    """
    
    def __init__(self, logger: MonitoringLogger, operation: str):
        """
        Initialize operation timer
        
        Args:
            logger: MonitoringLogger instance
            operation: Operation name
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
        self.extra_data = {}
    
    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log performance"""
        if self.start_time:
            duration = time.time() - self.start_time
            
            # Add exception info if operation failed
            if exc_type:
                self.extra_data['exception_type'] = exc_type.__name__
                self.extra_data['success'] = False
            else:
                self.extra_data['success'] = True
            
            self.logger.log_performance(self.operation, duration, **self.extra_data)
    
    def add_data(self, **kwargs):
        """Add extra data to be logged with performance metrics"""
        self.extra_data.update(kwargs)


class LogAnalyzer:
    """
    Log analysis and reporting utilities
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize log analyzer
        
        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
    
    def analyze_performance_logs(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze performance logs for specified time period
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dict: Performance analysis results
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            performance_data = []
            
            # Read performance log files
            perf_log_dir = self.log_dir / "performance"
            for log_file in perf_log_dir.glob("*performance*.log*"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line.strip())
                                log_time = datetime.fromisoformat(log_entry['timestamp'])
                                
                                if log_time >= cutoff_time:
                                    performance_data.append(log_entry)
                            except (json.JSONDecodeError, KeyError, ValueError):
                                continue
                except Exception:
                    continue
            
            # Analyze performance data
            analysis = {
                'time_period_hours': hours,
                'total_operations': len(performance_data),
                'operations_by_type': {},
                'performance_summary': {},
                'slowest_operations': [],
                'error_rate': 0
            }
            
            # Group by operation type
            operations = {}
            errors = 0
            
            for entry in performance_data:
                extra = entry.get('extra', {})
                operation = extra.get('operation', 'unknown')
                duration = extra.get('duration_seconds', 0)
                success = extra.get('success', True)
                
                if not success:
                    errors += 1
                
                if operation not in operations:
                    operations[operation] = []
                
                operations[operation].append({
                    'duration': duration,
                    'success': success,
                    'timestamp': entry['timestamp']
                })
            
            # Calculate statistics for each operation
            for operation, data in operations.items():
                durations = [d['duration'] for d in data]
                successes = [d['success'] for d in data]
                
                analysis['operations_by_type'][operation] = len(data)
                analysis['performance_summary'][operation] = {
                    'count': len(data),
                    'average_duration': sum(durations) / len(durations) if durations else 0,
                    'min_duration': min(durations) if durations else 0,
                    'max_duration': max(durations) if durations else 0,
                    'success_rate': sum(successes) / len(successes) * 100 if successes else 0
                }
            
            # Find slowest operations
            all_operations = []
            for operation, data in operations.items():
                for item in data:
                    all_operations.append({
                        'operation': operation,
                        'duration': item['duration'],
                        'timestamp': item['timestamp']
                    })
            
            analysis['slowest_operations'] = sorted(
                all_operations, 
                key=lambda x: x['duration'], 
                reverse=True
            )[:10]
            
            # Calculate error rate
            if performance_data:
                analysis['error_rate'] = (errors / len(performance_data)) * 100
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get error summary for specified time period
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dict: Error summary
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            errors = []
            
            # Read error log files
            error_log_dir = self.log_dir / "errors"
            for log_file in error_log_dir.glob("*errors*.log*"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line.strip())
                                log_time = datetime.fromisoformat(log_entry['timestamp'])
                                
                                if log_time >= cutoff_time:
                                    errors.append(log_entry)
                            except (json.JSONDecodeError, KeyError, ValueError):
                                continue
                except Exception:
                    continue
            
            # Analyze errors
            summary = {
                'time_period_hours': hours,
                'total_errors': len(errors),
                'errors_by_level': {},
                'errors_by_module': {},
                'recent_errors': errors[-10:] if errors else []
            }
            
            # Group by level and module
            for error in errors:
                level = error.get('level', 'UNKNOWN')
                module = error.get('module', 'unknown')
                
                summary['errors_by_level'][level] = summary['errors_by_level'].get(level, 0) + 1
                summary['errors_by_module'][module] = summary['errors_by_module'].get(module, 0) + 1
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}


# Global logger instance
_monitoring_logger = None


def get_monitoring_logger(name: str = "website_monitoring", log_dir: str = "logs") -> MonitoringLogger:
    """
    Get global monitoring logger instance
    
    Args:
        name: Logger name
        log_dir: Log directory
        
    Returns:
        MonitoringLogger: Logger instance
    """
    global _monitoring_logger
    
    if _monitoring_logger is None:
        _monitoring_logger = MonitoringLogger(name, log_dir)
    
    return _monitoring_logger


# Example usage and testing
def main():
    """
    Example usage of monitoring logger
    """
    # Initialize logger
    logger = get_monitoring_logger()
    
    # Test different log levels
    logger.log_info("System started", component="main", version="1.0.0")
    logger.log_warning("Configuration file not found, using defaults", config_file="config.json")
    
    # Test performance logging
    with logger.start_operation("test_operation") as timer:
        time.sleep(0.1)  # Simulate work
        timer.add_data(items_processed=100, success_rate=95.5)
    
    # Test audit logging
    logger.log_audit("system_configuration_changed", user="admin", changes={"interval": 60})
    
    # Test system health logging
    logger.log_system_health({
        'cpu_usage': 45.2,
        'memory_usage': 67.8,
        'disk_usage': 23.1,
        'active_connections': 5
    })
    
    # Get performance summary
    summary = logger.get_performance_summary()
    print("Performance Summary:")
    print(json.dumps(summary, indent=2))
    
    # Test log analysis
    analyzer = LogAnalyzer()
    perf_analysis = analyzer.analyze_performance_logs(1)  # Last 1 hour
    print("\nPerformance Analysis:")
    print(json.dumps(perf_analysis, indent=2))


if __name__ == "__main__":
    main()