#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Status Reporter for Website Monitoring
網站監控系統狀態報告器

This module provides comprehensive system status reporting capabilities,
including automated reports, status notifications, and trend analysis.
"""

import os
import sys
import json
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Import monitoring components
from monitoring_dashboard import MonitoringDashboard, SystemHealthChecker
from monitoring_logger import get_monitoring_logger, LogAnalyzer
from config_manager import ConfigManager
from email_sender import EmailSender


class StatusReportGenerator:
    """
    Generate comprehensive status reports
    
    Provides:
    - Daily/weekly/monthly status reports
    - Performance trend analysis
    - Health status summaries
    - Alert summaries
    - Visual charts and graphs
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize status report generator
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = get_monitoring_logger()
        
        # Initialize components
        self.dashboard = MonitoringDashboard(config_path)
        self.health_checker = SystemHealthChecker(self.logger)
        self.log_analyzer = LogAnalyzer()
        self.config_manager = ConfigManager(config_path, self.logger.main_logger)
        
        # Report configuration
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        
        # Chart configuration
        plt.style.use('default')
        
        self.logger.log_info("Status Report Generator initialized")
    
    def generate_daily_report(self, date: datetime = None) -> Dict[str, Any]:
        """
        Generate daily status report
        
        Args:
            date: Date for report (defaults to yesterday)
            
        Returns:
            Dict: Daily report data
        """
        try:
            if date is None:
                date = datetime.now() - timedelta(days=1)
            
            report_start = datetime.now()
            
            # Get data for the specified day
            start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            
            # Analyze performance for the day
            performance_analysis = self.log_analyzer.analyze_performance_logs(24)
            error_summary = self.log_analyzer.get_error_summary(24)
            
            # Get health check history
            health_history = self.health_checker.get_health_history(24)
            
            # Generate dashboard data
            dashboard_data = self.dashboard.generate_dashboard_data()
            
            # Compile daily report
            daily_report = {
                'report_type': 'daily',
                'report_date': date.strftime('%Y-%m-%d'),
                'generation_time': datetime.now().isoformat(),
                'summary': {
                    'total_operations': performance_analysis.get('total_operations', 0),
                    'success_rate': self._calculate_success_rate(performance_analysis),
                    'total_errors': error_summary.get('total_errors', 0),
                    'average_response_time': self._calculate_average_response_time(performance_analysis),
                    'health_checks_performed': len(health_history),
                    'system_uptime_hours': dashboard_data.get('system_status', {}).get('uptime_hours', 0)
                },
                'performance_details': performance_analysis,
                'error_details': error_summary,
                'health_status': self._analyze_health_trends(health_history),
                'alerts_summary': self._summarize_alerts(dashboard_data.get('alerts', [])),
                'recommendations': self._generate_daily_recommendations(
                    performance_analysis, error_summary, health_history
                )
            }
            
            # Add generation time
            daily_report['report_generation_time'] = (datetime.now() - report_start).total_seconds()
            
            self.logger.log_performance("daily_report_generation", daily_report['report_generation_time'])
            
            return daily_report
            
        except Exception as e:
            error_msg = f"Error generating daily report: {e}"
            self.logger.log_error(error_msg)
            return {
                'report_type': 'daily',
                'error': error_msg,
                'generation_time': datetime.now().isoformat()
            }
    
    def generate_weekly_report(self, week_start: datetime = None) -> Dict[str, Any]:
        """
        Generate weekly status report
        
        Args:
            week_start: Start date of week (defaults to last Monday)
            
        Returns:
            Dict: Weekly report data
        """
        try:
            if week_start is None:
                # Get last Monday
                today = datetime.now()
                days_since_monday = today.weekday()
                week_start = today - timedelta(days=days_since_monday + 7)
            
            report_start = datetime.now()
            
            # Generate daily reports for the week
            daily_reports = []
            weekly_summary = {
                'total_operations': 0,
                'total_errors': 0,
                'total_health_checks': 0,
                'daily_success_rates': [],
                'daily_response_times': [],
                'daily_error_counts': []
            }
            
            for day_offset in range(7):
                day = week_start + timedelta(days=day_offset)
                daily_report = self.generate_daily_report(day)
                daily_reports.append(daily_report)
                
                # Aggregate weekly data
                if 'error' not in daily_report:
                    summary = daily_report.get('summary', {})
                    weekly_summary['total_operations'] += summary.get('total_operations', 0)
                    weekly_summary['total_errors'] += summary.get('total_errors', 0)
                    weekly_summary['total_health_checks'] += summary.get('health_checks_performed', 0)
                    weekly_summary['daily_success_rates'].append(summary.get('success_rate', 0))
                    weekly_summary['daily_response_times'].append(summary.get('average_response_time', 0))
                    weekly_summary['daily_error_counts'].append(summary.get('total_errors', 0))
            
            # Calculate weekly averages
            weekly_avg_success_rate = (
                sum(weekly_summary['daily_success_rates']) / len(weekly_summary['daily_success_rates'])
                if weekly_summary['daily_success_rates'] else 0
            )
            
            weekly_avg_response_time = (
                sum(weekly_summary['daily_response_times']) / len(weekly_summary['daily_response_times'])
                if weekly_summary['daily_response_times'] else 0
            )
            
            # Compile weekly report
            weekly_report = {
                'report_type': 'weekly',
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': (week_start + timedelta(days=6)).strftime('%Y-%m-%d'),
                'generation_time': datetime.now().isoformat(),
                'summary': {
                    'total_operations': weekly_summary['total_operations'],
                    'average_success_rate': weekly_avg_success_rate,
                    'total_errors': weekly_summary['total_errors'],
                    'average_response_time': weekly_avg_response_time,
                    'total_health_checks': weekly_summary['total_health_checks']
                },
                'daily_reports': daily_reports,
                'trends': {
                    'success_rate_trend': self._calculate_trend(weekly_summary['daily_success_rates']),
                    'response_time_trend': self._calculate_trend(weekly_summary['daily_response_times']),
                    'error_count_trend': self._calculate_trend(weekly_summary['daily_error_counts'])
                },
                'recommendations': self._generate_weekly_recommendations(daily_reports)
            }
            
            # Add generation time
            weekly_report['report_generation_time'] = (datetime.now() - report_start).total_seconds()
            
            self.logger.log_performance("weekly_report_generation", weekly_report['report_generation_time'])
            
            return weekly_report
            
        except Exception as e:
            error_msg = f"Error generating weekly report: {e}"
            self.logger.log_error(error_msg)
            return {
                'report_type': 'weekly',
                'error': error_msg,
                'generation_time': datetime.now().isoformat()
            }
    
    def generate_performance_charts(self, report_data: Dict[str, Any], 
                                  output_dir: str = None) -> List[str]:
        """
        Generate performance charts for report
        
        Args:
            report_data: Report data to visualize
            output_dir: Output directory for charts
            
        Returns:
            List[str]: List of generated chart file paths
        """
        try:
            if output_dir is None:
                output_dir = self.report_dir / "charts"
            
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            chart_files = []
            
            # Generate charts based on report type
            if report_data.get('report_type') == 'weekly':
                chart_files.extend(self._generate_weekly_charts(report_data, output_path))
            elif report_data.get('report_type') == 'daily':
                chart_files.extend(self._generate_daily_charts(report_data, output_path))
            
            return chart_files
            
        except Exception as e:
            self.logger.log_error(f"Error generating performance charts: {e}")
            return []
    
    def _generate_weekly_charts(self, weekly_data: Dict[str, Any], 
                               output_path: Path) -> List[str]:
        """Generate charts for weekly report"""
        chart_files = []
        
        try:
            daily_reports = weekly_data.get('daily_reports', [])
            if not daily_reports:
                return chart_files
            
            # Extract data for charts
            dates = []
            success_rates = []
            response_times = []
            error_counts = []
            
            for daily_report in daily_reports:
                if 'error' not in daily_report:
                    dates.append(datetime.strptime(daily_report['report_date'], '%Y-%m-%d'))
                    summary = daily_report.get('summary', {})
                    success_rates.append(summary.get('success_rate', 0))
                    response_times.append(summary.get('average_response_time', 0))
                    error_counts.append(summary.get('total_errors', 0))
            
            if not dates:
                return chart_files
            
            # Success Rate Chart
            plt.figure(figsize=(12, 6))
            plt.plot(dates, success_rates, marker='o', linewidth=2, markersize=6)
            plt.title('Weekly Success Rate Trend', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Success Rate (%)')
            plt.grid(True, alpha=0.3)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            success_chart_file = output_path / f"weekly_success_rate_{weekly_data['week_start']}.png"
            plt.savefig(success_chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files.append(str(success_chart_file))
            
            # Response Time Chart
            plt.figure(figsize=(12, 6))
            plt.plot(dates, response_times, marker='s', color='orange', linewidth=2, markersize=6)
            plt.title('Weekly Response Time Trend', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Average Response Time (seconds)')
            plt.grid(True, alpha=0.3)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            response_chart_file = output_path / f"weekly_response_time_{weekly_data['week_start']}.png"
            plt.savefig(response_chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files.append(str(response_chart_file))
            
            # Error Count Chart
            plt.figure(figsize=(12, 6))
            plt.bar(dates, error_counts, color='red', alpha=0.7, width=0.8)
            plt.title('Weekly Error Count', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Number of Errors')
            plt.grid(True, alpha=0.3, axis='y')
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            error_chart_file = output_path / f"weekly_error_count_{weekly_data['week_start']}.png"
            plt.savefig(error_chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files.append(str(error_chart_file))
            
        except Exception as e:
            self.logger.log_error(f"Error generating weekly charts: {e}")
        
        return chart_files
    
    def _generate_daily_charts(self, daily_data: Dict[str, Any], 
                              output_path: Path) -> List[str]:
        """Generate charts for daily report"""
        chart_files = []
        
        try:
            performance_details = daily_data.get('performance_details', {})
            operations_by_type = performance_details.get('operations_by_type', {})
            
            if operations_by_type:
                # Operations Distribution Pie Chart
                plt.figure(figsize=(10, 8))
                labels = list(operations_by_type.keys())
                sizes = list(operations_by_type.values())
                colors = plt.cm.Set3(range(len(labels)))
                
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                plt.title(f'Operations Distribution - {daily_data["report_date"]}', 
                         fontsize=14, fontweight='bold')
                plt.axis('equal')
                
                pie_chart_file = output_path / f"daily_operations_{daily_data['report_date']}.png"
                plt.savefig(pie_chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files.append(str(pie_chart_file))
            
            # Error Distribution Chart
            error_details = daily_data.get('error_details', {})
            errors_by_level = error_details.get('errors_by_level', {})
            
            if errors_by_level:
                plt.figure(figsize=(10, 6))
                levels = list(errors_by_level.keys())
                counts = list(errors_by_level.values())
                colors = {'ERROR': 'red', 'WARNING': 'orange', 'CRITICAL': 'darkred'}
                bar_colors = [colors.get(level, 'gray') for level in levels]
                
                plt.bar(levels, counts, color=bar_colors, alpha=0.7)
                plt.title(f'Error Distribution by Level - {daily_data["report_date"]}', 
                         fontsize=14, fontweight='bold')
                plt.xlabel('Error Level')
                plt.ylabel('Number of Errors')
                plt.grid(True, alpha=0.3, axis='y')
                
                error_chart_file = output_path / f"daily_errors_{daily_data['report_date']}.png"
                plt.savefig(error_chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files.append(str(error_chart_file))
            
        except Exception as e:
            self.logger.log_error(f"Error generating daily charts: {e}")
        
        return chart_files
    
    def export_report(self, report_data: Dict[str, Any], 
                     format_type: str = 'json', 
                     include_charts: bool = True) -> str:
        """
        Export report to file
        
        Args:
            report_data: Report data to export
            format_type: Export format ('json', 'html')
            include_charts: Whether to include charts
            
        Returns:
            str: Path to exported report file
        """
        try:
            report_type = report_data.get('report_type', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format_type == 'json':
                output_file = self.report_dir / f"{report_type}_report_{timestamp}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
                
            elif format_type == 'html':
                output_file = self.report_dir / f"{report_type}_report_{timestamp}.html"
                html_content = self._generate_html_report(report_data, include_charts)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
            
            self.logger.log_audit("report_exported", 
                                report_type=report_type, 
                                format=format_type, 
                                output_file=str(output_file))
            
            return str(output_file)
            
        except Exception as e:
            error_msg = f"Error exporting report: {e}"
            self.logger.log_error(error_msg)
            return ""
    
    def _generate_html_report(self, report_data: Dict[str, Any], 
                             include_charts: bool = True) -> str:
        """Generate HTML report content"""
        
        report_type = report_data.get('report_type', 'Unknown')
        generation_time = report_data.get('generation_time', 'Unknown')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_type.title()} Monitoring Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .warning {{ background-color: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .error {{ background-color: #f8d7da; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 3px; }}
        .chart {{ text-align: center; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .recommendations {{ background-color: #d1ecf1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_type.title()} Monitoring Report</h1>
        <p><strong>Generated:</strong> {generation_time}</p>
    </div>
"""
        
        # Add summary section
        if 'summary' in report_data:
            summary = report_data['summary']
            html_content += f"""
    <div class="summary">
        <h2>Summary</h2>
        <div class="metric"><strong>Total Operations:</strong> {summary.get('total_operations', 0)}</div>
        <div class="metric"><strong>Success Rate:</strong> {summary.get('success_rate', 0):.1f}%</div>
        <div class="metric"><strong>Total Errors:</strong> {summary.get('total_errors', 0)}</div>
        <div class="metric"><strong>Avg Response Time:</strong> {summary.get('average_response_time', 0):.2f}s</div>
    </div>
"""
        
        # Add recommendations
        if 'recommendations' in report_data:
            recommendations = report_data['recommendations']
            html_content += """
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
"""
            for rec in recommendations:
                html_content += f"            <li>{rec}</li>\n"
            
            html_content += """        </ul>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        return html_content
    
    def _calculate_success_rate(self, performance_analysis: Dict[str, Any]) -> float:
        """Calculate success rate from performance analysis"""
        try:
            total_operations = performance_analysis.get('total_operations', 0)
            error_rate = performance_analysis.get('error_rate', 0)
            
            if total_operations > 0:
                return 100 - error_rate
            else:
                return 0
                
        except Exception:
            return 0
    
    def _calculate_average_response_time(self, performance_analysis: Dict[str, Any]) -> float:
        """Calculate average response time from performance analysis"""
        try:
            performance_summary = performance_analysis.get('performance_summary', {})
            
            if performance_summary:
                response_times = [
                    metrics.get('average_duration', 0) 
                    for metrics in performance_summary.values()
                ]
                return sum(response_times) / len(response_times) if response_times else 0
            else:
                return 0
                
        except Exception:
            return 0
    
    def _analyze_health_trends(self, health_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze health check trends"""
        try:
            if not health_history:
                return {'status': 'no_data'}
            
            # Count status occurrences
            status_counts = {'healthy': 0, 'warning': 0, 'critical': 0}
            
            for health_check in health_history:
                status = health_check.get('overall_status', 'unknown')
                if status in status_counts:
                    status_counts[status] += 1
            
            total_checks = len(health_history)
            
            return {
                'total_checks': total_checks,
                'status_distribution': status_counts,
                'health_percentage': (status_counts['healthy'] / total_checks * 100) if total_checks > 0 else 0,
                'latest_status': health_history[-1].get('overall_status', 'unknown') if health_history else 'unknown'
            }
            
        except Exception as e:
            self.logger.log_error(f"Error analyzing health trends: {e}")
            return {'error': str(e)}
    
    def _summarize_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize alerts by type and level"""
        try:
            summary = {
                'total_alerts': len(alerts),
                'by_level': {'critical': 0, 'warning': 0, 'info': 0},
                'by_type': {}
            }
            
            for alert in alerts:
                level = alert.get('level', 'info')
                alert_type = alert.get('type', 'unknown')
                
                if level in summary['by_level']:
                    summary['by_level'][level] += 1
                
                summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from list of values"""
        try:
            if len(values) < 2:
                return 'stable'
            
            # Simple trend calculation
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg * 1.05:
                return 'increasing'
            elif second_avg < first_avg * 0.95:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception:
            return 'unknown'
    
    def _generate_daily_recommendations(self, performance_analysis: Dict, 
                                      error_summary: Dict, 
                                      health_history: List) -> List[str]:
        """Generate recommendations for daily report"""
        recommendations = []
        
        try:
            # Performance-based recommendations
            error_rate = performance_analysis.get('error_rate', 0)
            if error_rate > 10:
                recommendations.append(f"High error rate ({error_rate:.1f}%) - investigate and fix recurring issues")
            
            # Error-based recommendations
            total_errors = error_summary.get('total_errors', 0)
            if total_errors > 20:
                recommendations.append(f"High error count ({total_errors}) - review error logs for patterns")
            
            # Health-based recommendations
            if health_history:
                critical_checks = sum(1 for h in health_history if h.get('overall_status') == 'critical')
                if critical_checks > len(health_history) * 0.2:
                    recommendations.append("Frequent critical health status - check system resources")
            
            if not recommendations:
                recommendations.append("System performance is within normal parameters")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _generate_weekly_recommendations(self, daily_reports: List[Dict]) -> List[str]:
        """Generate recommendations for weekly report"""
        recommendations = []
        
        try:
            # Analyze trends across the week
            success_rates = []
            error_counts = []
            
            for report in daily_reports:
                if 'error' not in report:
                    summary = report.get('summary', {})
                    success_rates.append(summary.get('success_rate', 0))
                    error_counts.append(summary.get('total_errors', 0))
            
            if success_rates:
                avg_success_rate = sum(success_rates) / len(success_rates)
                if avg_success_rate < 90:
                    recommendations.append(f"Weekly average success rate ({avg_success_rate:.1f}%) below target - investigate reliability issues")
            
            if error_counts:
                total_weekly_errors = sum(error_counts)
                if total_weekly_errors > 100:
                    recommendations.append(f"High weekly error count ({total_weekly_errors}) - implement error reduction measures")
            
            if not recommendations:
                recommendations.append("Weekly performance trends are satisfactory")
            
        except Exception as e:
            recommendations.append(f"Error generating weekly recommendations: {e}")
        
        return recommendations


class AutomatedReporter:
    """
    Automated status reporting system
    
    Provides:
    - Scheduled report generation
    - Automatic email delivery
    - Report archival
    - Alert-based reporting
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize automated reporter
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = get_monitoring_logger()
        
        # Initialize components
        self.report_generator = StatusReportGenerator(config_path)
        self.config_manager = ConfigManager(config_path, self.logger.main_logger)
        
        # Email sender for report delivery
        try:
            self.email_sender = EmailSender(
                config=self.config_manager.get_config(),
                logger=self.logger.main_logger
            )
        except Exception as e:
            self.logger.log_warning(f"Email sender initialization failed: {e}")
            self.email_sender = None
        
        self.logger.log_info("Automated Reporter initialized")
    
    def send_daily_report(self, recipients: List[str] = None) -> Tuple[bool, str]:
        """
        Generate and send daily report
        
        Args:
            recipients: Email recipients (uses config default if None)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Generate daily report
            daily_report = self.report_generator.generate_daily_report()
            
            if 'error' in daily_report:
                return False, f"Failed to generate daily report: {daily_report['error']}"
            
            # Export report
            report_file = self.report_generator.export_report(daily_report, 'html', True)
            
            if not report_file:
                return False, "Failed to export daily report"
            
            # Send email if email sender is available
            if self.email_sender and recipients:
                subject = f"Daily Monitoring Report - {daily_report['report_date']}"
                
                # Create email body
                summary = daily_report.get('summary', {})
                body = f"""
Daily Monitoring Report for {daily_report['report_date']}

Summary:
- Total Operations: {summary.get('total_operations', 0)}
- Success Rate: {summary.get('success_rate', 0):.1f}%
- Total Errors: {summary.get('total_errors', 0)}
- Average Response Time: {summary.get('average_response_time', 0):.2f} seconds

Please see the attached detailed report for more information.
"""
                
                success = self.email_sender.send_email_with_attachment(
                    recipients, subject, body, report_file
                )
                
                if success:
                    self.logger.log_audit("daily_report_sent", recipients=recipients)
                    return True, f"Daily report generated and sent to {len(recipients)} recipients"
                else:
                    return False, "Daily report generated but email delivery failed"
            else:
                return True, f"Daily report generated: {report_file}"
                
        except Exception as e:
            error_msg = f"Error sending daily report: {e}"
            self.logger.log_error(error_msg)
            return False, error_msg
    
    def send_weekly_report(self, recipients: List[str] = None) -> Tuple[bool, str]:
        """
        Generate and send weekly report
        
        Args:
            recipients: Email recipients (uses config default if None)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Generate weekly report
            weekly_report = self.report_generator.generate_weekly_report()
            
            if 'error' in weekly_report:
                return False, f"Failed to generate weekly report: {weekly_report['error']}"
            
            # Generate charts
            chart_files = self.report_generator.generate_performance_charts(weekly_report)
            
            # Export report
            report_file = self.report_generator.export_report(weekly_report, 'html', True)
            
            if not report_file:
                return False, "Failed to export weekly report"
            
            # Send email if email sender is available
            if self.email_sender and recipients:
                subject = f"Weekly Monitoring Report - {weekly_report['week_start']} to {weekly_report['week_end']}"
                
                # Create email body
                summary = weekly_report.get('summary', {})
                body = f"""
Weekly Monitoring Report for {weekly_report['week_start']} to {weekly_report['week_end']}

Summary:
- Total Operations: {summary.get('total_operations', 0)}
- Average Success Rate: {summary.get('average_success_rate', 0):.1f}%
- Total Errors: {summary.get('total_errors', 0)}
- Average Response Time: {summary.get('average_response_time', 0):.2f} seconds

Trends:
- Success Rate: {weekly_report.get('trends', {}).get('success_rate_trend', 'unknown')}
- Response Time: {weekly_report.get('trends', {}).get('response_time_trend', 'unknown')}
- Error Count: {weekly_report.get('trends', {}).get('error_count_trend', 'unknown')}

Please see the attached detailed report and charts for more information.
"""
                
                # Attach report and charts
                attachments = [report_file] + chart_files
                
                success = self.email_sender.send_email_with_attachments(
                    recipients, subject, body, attachments
                )
                
                if success:
                    self.logger.log_audit("weekly_report_sent", recipients=recipients)
                    return True, f"Weekly report generated and sent to {len(recipients)} recipients"
                else:
                    return False, "Weekly report generated but email delivery failed"
            else:
                return True, f"Weekly report generated: {report_file}"
                
        except Exception as e:
            error_msg = f"Error sending weekly report: {e}"
            self.logger.log_error(error_msg)
            return False, error_msg


def main():
    """
    Main status reporter entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='System Status Reporter')
    parser.add_argument(
        'action',
        choices=['daily', 'weekly', 'send-daily', 'send-weekly'],
        help='Report action to perform'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'html'],
        default='html',
        help='Report format (default: html)'
    )
    parser.add_argument(
        '--recipients', '-r',
        nargs='+',
        help='Email recipients for send actions'
    )
    
    args = parser.parse_args()
    
    try:
        if args.action in ['daily', 'weekly']:
            # Generate report
            generator = StatusReportGenerator(args.config)
            
            if args.action == 'daily':
                report = generator.generate_daily_report()
                print("Daily Report Generated:")
            else:
                report = generator.generate_weekly_report()
                print("Weekly Report Generated:")
            
            if 'error' in report:
                print(f"✗ Error: {report['error']}")
                return 1
            
            # Export report
            output_file = generator.export_report(report, args.format, True)
            if output_file:
                print(f"✓ Report exported to: {output_file}")
            else:
                print("✗ Failed to export report")
                return 1
        
        elif args.action in ['send-daily', 'send-weekly']:
            # Send report via email
            reporter = AutomatedReporter(args.config)
            
            if not args.recipients:
                print("✗ Recipients required for send actions")
                return 1
            
            if args.action == 'send-daily':
                success, message = reporter.send_daily_report(args.recipients)
            else:
                success, message = reporter.send_weekly_report(args.recipients)
            
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"✗ Status reporter error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())