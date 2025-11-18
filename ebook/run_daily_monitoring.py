#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Monitoring Execution Script
每日監控執行腳本

This script is designed to be called by the Node.js scheduler to execute
a complete monitoring cycle including all scrapers and processors.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Import monitoring components
from monitoring_controller import MonitoringController
from config_manager import ConfigManager


def setup_logging():
    """Set up logging for daily monitoring execution"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"daily_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """
    Main execution function for daily monitoring
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = setup_logging()
    
    try:
        logger.info("=" * 80)
        logger.info("Starting Daily Monitoring Execution")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # Initialize configuration manager
        config_path = "config.json"
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return 1
        
        logger.info(f"Loading configuration from: {config_path}")
        config_manager = ConfigManager(config_path, logger)
        
        # Initialize monitoring controller
        logger.info("Initializing monitoring controller...")
        controller = MonitoringController(config_path, logger)
        
        # Initialize system
        logger.info("Initializing monitoring system...")
        success, message = controller.initialize_system()
        if not success:
            logger.error(f"System initialization failed: {message}")
            return 1
        
        logger.info(f"System initialization successful: {message}")
        
        # Execute single monitoring cycle
        logger.info("Executing monitoring cycle...")
        logger.info("-" * 80)
        
        # Get website monitor instance
        website_monitor = controller.website_monitor
        
        # Run single monitoring cycle
        cycle_success = website_monitor.start_monitoring_cycle()
        
        logger.info("-" * 80)
        
        # Send email notification if configured
        try:
            from email_sender import EmailSender
            email_config = config_manager.get_config().get('email', {})
            
            if email_config.get('enabled', False):
                logger.info("Sending email notification...")
                email_sender = EmailSender(config_manager.get_config(), logger)
                
                # Get monitoring statistics
                stats = website_monitor.monitoring_stats
                
                # Prepare email content
                email_subject = f"【每日監控報告】{datetime.now().strftime('%Y-%m-%d')} 網站監控執行完成"
                email_body = f"""
每日網站監控執行報告

執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
執行狀態：{'成功' if cycle_success else '失敗'}

監控統計：
- 完成週期數：{stats.get('cycles_completed', 0)}
- 處理內容總數：{stats.get('total_content_processed', 0)}
- 錯誤次數：{stats.get('errors_encountered', 0)}

詳細資訊請查看系統日誌。

此郵件由系統自動發送，請勿回覆。
                """.strip()
                
                email_sender.send_notification_email(
                    subject=email_subject,
                    body=email_body,
                    is_html=False
                )
                logger.info("Email notification sent successfully")
        except Exception as email_error:
            logger.warning(f"Failed to send email notification: {email_error}")
            # Don't fail the whole process if email fails
        
        if cycle_success:
            logger.info("✅ Monitoring cycle completed successfully")
            
            # Get monitoring statistics
            stats = website_monitor.monitoring_stats
            logger.info(f"Monitoring Statistics:")
            logger.info(f"  - Cycles completed: {stats.get('cycles_completed', 0)}")
            logger.info(f"  - Total content processed: {stats.get('total_content_processed', 0)}")
            logger.info(f"  - Errors encountered: {stats.get('errors_encountered', 0)}")
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            logger.info(f"  - Execution time: {execution_time:.2f} seconds")
            
            # Generate output summary for Node.js integration
            output_summary = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "statistics": {
                    "cycles_completed": stats.get('cycles_completed', 0),
                    "total_content_processed": stats.get('total_content_processed', 0),
                    "errors_encountered": stats.get('errors_encountered', 0),
                    "last_successful_cycle": stats.get('last_successful_cycle').isoformat() if stats.get('last_successful_cycle') else None,
                    "average_cycle_time": stats.get('average_cycle_time', 0)
                },
                "message": "Monitoring cycle completed successfully"
            }
            
            # Write summary to output file for Node.js to read
            output_dir = Path("generated_documents")
            output_dir.mkdir(exist_ok=True)
            
            summary_file = output_dir / f"monitoring_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(output_summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Summary written to: {summary_file}")
            
            logger.info("=" * 80)
            logger.info("Daily Monitoring Execution Completed Successfully")
            logger.info("=" * 80)
            
            return 0
            
        else:
            logger.error("❌ Monitoring cycle failed")
            
            # Generate error output
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            output_summary = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "message": "Monitoring cycle failed",
                "error": "Cycle execution returned failure status"
            }
            
            output_dir = Path("generated_documents")
            output_dir.mkdir(exist_ok=True)
            
            summary_file = output_dir / f"monitoring_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(output_summary, f, ensure_ascii=False, indent=2)
            
            logger.error("=" * 80)
            logger.error("Daily Monitoring Execution Failed")
            logger.error("=" * 80)
            
            return 1
        
    except Exception as e:
        logger.error(f"💥 Unexpected error during daily monitoring: {e}", exc_info=True)
        
        # Generate error output
        try:
            output_summary = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "message": "Monitoring execution error",
                "error": str(e)
            }
            
            output_dir = Path("generated_documents")
            output_dir.mkdir(exist_ok=True)
            
            summary_file = output_dir / f"monitoring_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(output_summary, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        return 1
    
    finally:
        # Cleanup
        try:
            if 'website_monitor' in locals() and website_monitor:
                logger.info("Cleaning up monitoring resources...")
                # Clean up individual scrapers and processors
                if hasattr(website_monitor, 'scrapers'):
                    for scraper_name, scraper in website_monitor.scrapers.items():
                        try:
                            if hasattr(scraper, 'cleanup'):
                                scraper.cleanup()
                                logger.info(f"Cleaned up {scraper_name}")
                        except Exception as e:
                            logger.warning(f"Error cleaning up {scraper_name}: {e}")
                
                if hasattr(website_monitor, 'processors'):
                    for processor_name, processor in website_monitor.processors.items():
                        try:
                            if hasattr(processor, 'cleanup'):
                                processor.cleanup()
                                logger.info(f"Cleaned up {processor_name}")
                        except Exception as e:
                            logger.warning(f"Error cleaning up {processor_name}: {e}")
                
                logger.info("Cleanup completed")
        except Exception as cleanup_error:
            logger.warning(f"Cleanup error: {cleanup_error}")


if __name__ == "__main__":
    sys.exit(main())
