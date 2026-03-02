# Comprehensive Monitoring and Logging Guide
# 綜合監控與日誌指南

## Overview

This guide documents the comprehensive logging and monitoring infrastructure for the website monitoring system. The system integrates multiple monitoring components to provide real-time insights, health checks, performance metrics, and automated reporting.

## Architecture

### Component Overview

```
Comprehensive Monitoring System
├── Enhanced Monitoring Logger
│   ├── Real-time metrics collection
│   ├── Performance tracking
│   ├── Automated alerting
│   └── Structured logging
├── Enhanced Health Monitor
│   ├── Continuous health checks
│   ├── Trend analysis
│   ├── Component health tracking
│   └── Predictive alerting
├── Monitoring Dashboard
│   ├── System status visualization
│   ├── Performance metrics
│   └── Alert management
└── Status Reporter
    ├── Daily/weekly reports
    ├── Performance charts
    └── Email delivery
```

## Features

### 1. Enhanced Logging Infrastructure

**File**: `enhanced_monitoring_logger.py`

#### Capabilities
- **Structured Logging**: JSON-formatted logs with comprehensive metadata
- **Real-time Monitoring**: Continuous collection of system and performance metrics
- **Automated Alerting**: Threshold-based alerts for critical conditions
- **Performance Tracking**: Operation timing and performance metrics
- **Log Rotation**: Automatic log file management and cleanup

#### Usage

```python
from enhanced_monitoring_logger import get_enhanced_monitoring_logger

# Initialize logger
logger = get_enhanced_monitoring_logger()

# Start real-time monitoring
logger.start_real_time_monitoring(60)  # 60 second intervals

# Log with enhanced features
logger.log_info("Operation started", component="scraper", items=10)
logger.log_component_health("carousel_scraper", "healthy", cycles=5)
logger.log_monitoring_cycle("carousel", True, 2.5, items_found=3)

# Get real-time metrics
metrics = logger.get_real_time_metrics()

# Generate health report
health_report = logger.generate_health_report()
```

#### Log Locations

```
logs/
├── website_monitoring_enhanced_main.log       # Main application logs
├── website_monitoring_enhanced_daily.log      # Daily rotating logs
├── performance/
│   ├── website_monitoring_enhanced_performance.log
│   └── website_monitoring_enhanced_performance_daily.log
├── errors/
│   ├── website_monitoring_enhanced_errors.log
│   └── website_monitoring_enhanced_critical.log
└── audit/
    ├── website_monitoring_enhanced_audit.log
    └── website_monitoring_enhanced_audit_daily.log
```

### 2. Enhanced Health Monitoring

**File**: `enhanced_health_monitor.py`

#### Capabilities
- **Continuous Health Checks**: Automated health monitoring at configurable intervals
- **Trend Analysis**: Historical health data analysis and trend detection
- **Component Tracking**: Individual component health status
- **Predictive Alerting**: Early warning system for degrading health
- **Health Scoring**: 0-100 health score calculation

#### Usage

```python
from enhanced_health_monitor import EnhancedHealthMonitor

# Initialize health monitor
monitor = EnhancedHealthMonitor("config.json")

# Start continuous monitoring
monitor.start_continuous_monitoring(300)  # 5 minute intervals

# Perform manual health check
health_report = monitor.perform_health_check()

# Analyze trends
trends = monitor.analyze_health_trends(24)  # Last 24 hours

# Get health summary
summary = monitor.get_health_summary()

# Export health report
output_file = monitor.export_health_report()
```

#### Health Check Components

1. **System Resources**
   - CPU usage
   - Memory usage
   - Disk usage
   - Network statistics

2. **Application Health**
   - Error rates
   - Response times
   - Success rates
   - Component status

3. **Connectivity**
   - Website accessibility
   - ChromeDriver availability
   - External service connectivity

### 3. Comprehensive Monitoring Integration

**File**: `comprehensive_monitoring_integration.py`

#### Capabilities
- **Unified System**: Integrates all monitoring components
- **Comprehensive Status**: Single source of truth for system status
- **Automated Reporting**: Daily and weekly report generation
- **Email Delivery**: Automated report distribution
- **Centralized Control**: Single interface for all monitoring operations

#### Usage

```python
from comprehensive_monitoring_integration import ComprehensiveMonitoringSystem

# Initialize system
system = ComprehensiveMonitoringSystem("config.json")

# Initialize and start monitoring
success, message = system.initialize_system()
success, message = system.start_monitoring(60)  # 60 minute intervals

# Get comprehensive status
status = system.get_comprehensive_status()

# Generate reports
daily_report = system.generate_comprehensive_report('daily')
weekly_report = system.generate_comprehensive_report('weekly')

# Export reports
output_file = system.export_comprehensive_report('daily')

# Send email reports
success, message = system.send_status_email('daily', ['admin@example.com'])

# Cleanup
system.cleanup()
```

## Command-Line Interface

### Enhanced Monitoring Logger

```bash
# Test enhanced logger
python enhanced_monitoring_logger.py

# The script will:
# - Start real-time monitoring
# - Log test operations
# - Display metrics and health report
```

### Enhanced Health Monitor

```bash
# Start continuous health monitoring
python enhanced_health_monitor.py start --interval 300

# Perform single health check
python enhanced_health_monitor.py check

# Get health summary
python enhanced_health_monitor.py summary

# Analyze trends
python enhanced_health_monitor.py trends --hours 24

# Export health report
python enhanced_health_monitor.py export --output health_report.json
```

### Comprehensive Monitoring System

```bash
# Start monitoring
python comprehensive_monitoring_integration.py start --interval 60

# Stop monitoring
python comprehensive_monitoring_integration.py stop

# Get system status
python comprehensive_monitoring_integration.py status

# Generate and export report
python comprehensive_monitoring_integration.py report --type daily --output report.json

# Send email report
python comprehensive_monitoring_integration.py email --type weekly --recipients admin@example.com

# Perform health check
python comprehensive_monitoring_integration.py health
```

## Monitoring Metrics

### Performance Metrics

1. **Operation Metrics**
   - Operation count
   - Average duration
   - Min/max duration
   - Success rate
   - Last execution time

2. **System Metrics**
   - CPU usage percentage
   - Memory usage percentage
   - Disk usage percentage
   - Available memory (GB)
   - Free disk space (GB)

3. **Application Metrics**
   - Monitoring cycles completed
   - Success rate
   - Error rate
   - Average cycle time
   - Uptime hours

### Health Metrics

1. **Health Score** (0-100)
   - 90-100: Excellent
   - 70-89: Good
   - 50-69: Fair
   - 30-49: Poor
   - 0-29: Critical

2. **Component Health**
   - Healthy: Operating normally
   - Warning: Minor issues detected
   - Critical: Immediate attention required
   - Unknown: Status unavailable

## Alert Thresholds

### Default Thresholds

```python
{
    'error_rate_warning': 5.0,      # 5% error rate
    'error_rate_critical': 15.0,    # 15% error rate
    'response_time_warning': 30.0,  # 30 seconds
    'response_time_critical': 60.0, # 60 seconds
    'cpu_usage_warning': 80.0,      # 80% CPU
    'cpu_usage_critical': 95.0,     # 95% CPU
    'memory_usage_warning': 85.0,   # 85% memory
    'memory_usage_critical': 95.0   # 95% memory
}
```

### Customizing Thresholds

```python
from enhanced_monitoring_logger import get_enhanced_monitoring_logger

logger = get_enhanced_monitoring_logger()

# Update thresholds
logger.update_alert_thresholds({
    'cpu_usage_warning': 70.0,
    'memory_usage_warning': 80.0
})
```

## Report Types

### Daily Report

Generated for the previous day, includes:
- Total operations
- Success rate
- Error summary
- Average response time
- Health checks performed
- System uptime
- Recommendations

### Weekly Report

Generated for the previous week, includes:
- Daily summaries
- Weekly aggregates
- Trend analysis
- Performance charts
- Comprehensive recommendations

## Integration with Existing Infrastructure

### Existing Components Used

1. **MonitoringLogger** (`monitoring_logger.py`)
   - Base logging infrastructure
   - Structured logging
   - Log rotation
   - Performance tracking

2. **SystemHealthChecker** (`monitoring_dashboard.py`)
   - System resource monitoring
   - Application health checks
   - Connectivity checks

3. **MonitoringController** (`monitoring_controller.py`)
   - System lifecycle management
   - Configuration management
   - Performance metrics

4. **StatusReportGenerator** (`system_status_reporter.py`)
   - Report generation
   - Chart creation
   - Email delivery

### Enhanced Features

1. **Real-time Monitoring**
   - Continuous metrics collection
   - Live performance tracking
   - Immediate alert generation

2. **Predictive Analysis**
   - Trend detection
   - Health degradation prediction
   - Proactive recommendations

3. **Comprehensive Integration**
   - Unified monitoring interface
   - Centralized status reporting
   - Automated report distribution

## Best Practices

### 1. Monitoring Intervals

- **Real-time Metrics**: 30-60 seconds
- **Health Checks**: 5-10 minutes
- **Website Monitoring**: 30-60 minutes
- **Report Generation**: Daily/Weekly

### 2. Log Management

- Enable log rotation to prevent disk space issues
- Clean up old logs regularly (30-90 days)
- Monitor log file sizes
- Archive important logs for compliance

### 3. Alert Management

- Set appropriate thresholds for your environment
- Use alert cooldown to prevent alert fatigue
- Review and adjust thresholds based on trends
- Document alert response procedures

### 4. Performance Optimization

- Monitor system resources regularly
- Adjust monitoring intervals based on load
- Use parallel processing for independent operations
- Implement caching where appropriate

### 5. Health Monitoring

- Perform regular health checks
- Analyze trends to identify issues early
- Act on recommendations promptly
- Document health incidents and resolutions

## Troubleshooting

### High CPU Usage

```python
# Check real-time metrics
logger = get_enhanced_monitoring_logger()
metrics = logger.get_real_time_metrics()

# Review system resources
system_resources = metrics['metrics']['system_resources']

# Adjust monitoring intervals if needed
logger.stop_real_time_monitoring()
logger.start_real_time_monitoring(120)  # Increase to 2 minutes
```

### High Memory Usage

```python
# Check health report
monitor = EnhancedHealthMonitor()
health_report = monitor.perform_health_check()

# Review memory usage
memory_usage = health_report['system_resources']['memory']['usage_percent']

# Clean up old logs
logger.cleanup_old_logs(30)  # Keep only 30 days
```

### Alert Fatigue

```python
# Increase alert cooldown
monitor = EnhancedHealthMonitor()
monitor.alert_cooldown_seconds = 3600  # 1 hour

# Adjust thresholds
logger.update_alert_thresholds({
    'error_rate_warning': 10.0,  # Increase from 5.0
    'cpu_usage_warning': 90.0    # Increase from 80.0
})
```

### Missing Logs

```python
# Check log statistics
logger = get_enhanced_monitoring_logger()
health_report = logger.generate_health_report()
log_stats = health_report['log_statistics']

# Verify log directories exist
import os
os.makedirs('logs/performance', exist_ok=True)
os.makedirs('logs/errors', exist_ok=True)
os.makedirs('logs/audit', exist_ok=True)
```

## Requirements

### Python Packages

```
psutil>=5.8.0          # System resource monitoring
matplotlib>=3.3.0      # Chart generation
requests>=2.25.0       # HTTP connectivity checks
```

### Existing Dependencies

All existing monitoring infrastructure components:
- monitoring_logger.py
- monitoring_controller.py
- monitoring_dashboard.py
- system_status_reporter.py
- website_monitor.py
- config_manager.py

## Configuration

### Monitoring Configuration

Add to `config.json`:

```json
{
  "website_monitoring": {
    "enabled": true,
    "monitoring_interval": 3600,
    "enhanced_logging": {
      "enabled": true,
      "real_time_monitoring": true,
      "real_time_interval": 60,
      "log_retention_days": 30
    },
    "health_monitoring": {
      "enabled": true,
      "check_interval": 300,
      "alert_cooldown": 1800,
      "health_score_threshold": 70
    },
    "reporting": {
      "daily_reports": true,
      "weekly_reports": true,
      "email_recipients": ["admin@example.com"],
      "include_charts": true
    }
  }
}
```

## Summary

The comprehensive monitoring and logging infrastructure provides:

✓ **Real-time Monitoring**: Continuous metrics collection and analysis
✓ **Health Checks**: Automated system health monitoring
✓ **Performance Tracking**: Detailed operation and system metrics
✓ **Automated Alerting**: Threshold-based alerts for critical conditions
✓ **Comprehensive Reporting**: Daily and weekly status reports
✓ **Email Delivery**: Automated report distribution
✓ **Trend Analysis**: Historical data analysis and predictions
✓ **Integration**: Seamless integration with existing infrastructure

This system ensures comprehensive visibility into the website monitoring system's health, performance, and operational status.
