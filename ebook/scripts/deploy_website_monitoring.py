#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Monitoring Deployment Script
網站監控部署腳本

This script handles deployment preparation, configuration setup, and system validation
for the website monitoring system.
"""

import os
import sys
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import configuration and monitoring components
from config_manager import ConfigManager
from monitoring_controller import MonitoringController


class WebsiteMonitoringDeployer:
    """
    Deployment manager for website monitoring system
    
    Handles:
    - Environment setup and validation
    - Configuration template deployment
    - System initialization and testing
    - Scheduling integration setup
    - Health check configuration
    """
    
    def __init__(self, target_dir: str = ".", logger: Optional[logging.Logger] = None):
        """
        Initialize deployment manager
        
        Args:
            target_dir: Target deployment directory
            logger: Logger instance for deployment operations
        """
        self.target_dir = os.path.abspath(target_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        # Deployment configuration
        self.deployment_config = {
            'required_files': [
                'website_monitor.py',
                'monitoring_controller.py',
                'config_manager.py',
                'carousel_scraper.py',
                'bulletin_scraper.py',
                'news_processor.py',
                'media_processor.py',
                'enhanced_data_synchronizer.py',
                'notification_processor.py',
                'website_monitoring_cli.py'
            ],
            'required_directories': [
                'logs',
                'generated_documents',
                'generated_documents/website_monitoring',
                'downloads',
                'chromedriver-win64'
            ],
            'config_templates': {
                'config_template.json': 'config.json',
                'monitoring_config_template.json': 'monitoring_config.json'
            }
        }
        
        self.logger.info(f"Website Monitoring Deployer initialized for: {self.target_dir}")
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate deployment environment
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        try:
            self.logger.info("Validating deployment environment...")
            
            # Check Python version
            if sys.version_info < (3, 8):
                errors.append(f"Python 3.8+ required, found {sys.version}")
            
            # Check target directory
            if not os.path.exists(self.target_dir):
                try:
                    os.makedirs(self.target_dir, exist_ok=True)
                    self.logger.info(f"Created target directory: {self.target_dir}")
                except Exception as e:
                    errors.append(f"Cannot create target directory: {e}")
            
            # Check required files
            for required_file in self.deployment_config['required_files']:
                file_path = os.path.join(self.target_dir, required_file)
                if not os.path.exists(file_path):
                    errors.append(f"Required file missing: {required_file}")
            
            # Check ChromeDriver
            chromedriver_dir = os.path.join(self.target_dir, 'chromedriver-win64')
            chromedriver_exe = os.path.join(chromedriver_dir, 'chromedriver.exe')
            if not os.path.exists(chromedriver_exe):
                errors.append("ChromeDriver executable not found in chromedriver-win64/")
            
            # Check Python dependencies
            try:
                import selenium
                import google.generativeai
                self.logger.info("Core dependencies available")
            except ImportError as e:
                errors.append(f"Missing Python dependency: {e}")
            
            # Validate write permissions
            test_file = os.path.join(self.target_dir, 'deployment_test.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                errors.append(f"No write permission in target directory: {e}")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                self.logger.info("Environment validation passed")
            else:
                self.logger.error(f"Environment validation failed: {len(errors)} errors")
                for error in errors:
                    self.logger.error(f"  - {error}")
            
            return is_valid, errors
            
        except Exception as e:
            error_msg = f"Error during environment validation: {e}"
            self.logger.error(error_msg)
            return False, [error_msg]
    
    def setup_directory_structure(self) -> bool:
        """
        Create required directory structure
        
        Returns:
            bool: True if setup successful
        """
        try:
            self.logger.info("Setting up directory structure...")
            
            for directory in self.deployment_config['required_directories']:
                dir_path = os.path.join(self.target_dir, directory)
                
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    self.logger.info(f"Created directory: {directory}")
                else:
                    self.logger.debug(f"Directory already exists: {directory}")
            
            # Create additional subdirectories for monitoring data
            monitoring_subdirs = [
                'generated_documents/website_monitoring/carousel',
                'generated_documents/website_monitoring/cancellation',
                'generated_documents/website_monitoring/news',
                'generated_documents/website_monitoring/media',
                'logs/website_monitoring'
            ]
            
            for subdir in monitoring_subdirs:
                subdir_path = os.path.join(self.target_dir, subdir)
                if not os.path.exists(subdir_path):
                    os.makedirs(subdir_path, exist_ok=True)
                    self.logger.debug(f"Created monitoring subdirectory: {subdir}")
            
            self.logger.info("Directory structure setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up directory structure: {e}")
            return False
    
    def deploy_configuration_templates(self) -> bool:
        """
        Deploy configuration templates
        
        Returns:
            bool: True if deployment successful
        """
        try:
            self.logger.info("Deploying configuration templates...")
            
            # Create monitoring configuration template
            monitoring_template = self._create_monitoring_config_template()
            
            template_path = os.path.join(self.target_dir, 'monitoring_config_template.json')
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(monitoring_template, f, ensure_ascii=False, indent=2)
            
            self.logger.info("Created monitoring configuration template")
            
            # Create deployment configuration file
            deployment_info = {
                'deployment_date': datetime.now().isoformat(),
                'deployment_version': '1.0.0',
                'target_directory': self.target_dir,
                'python_version': sys.version,
                'required_files': self.deployment_config['required_files'],
                'configuration': {
                    'monitoring_enabled': False,
                    'chrome_devtools_enabled': False,
                    'content_types': {
                        'carousel': True,
                        'cancellation': True,
                        'news': True,
                        'media': True
                    }
                }
            }
            
            deployment_info_path = os.path.join(self.target_dir, 'deployment_info.json')
            with open(deployment_info_path, 'w', encoding='utf-8') as f:
                json.dump(deployment_info, f, ensure_ascii=False, indent=2)
            
            self.logger.info("Created deployment information file")
            
            # Create CLI wrapper scripts
            self._create_cli_wrapper_scripts()
            
            self.logger.info("Configuration templates deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying configuration templates: {e}")
            return False
    
    def _create_monitoring_config_template(self) -> Dict[str, Any]:
        """
        Create monitoring configuration template
        
        Returns:
            Dict: Monitoring configuration template
        """
        return {
            "website_monitoring": {
                "enabled": False,
                "monitoring_interval": 3600,
                "content_types": {
                    "carousel": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/",
                        "description": "Homepage carousel banner monitoring"
                    },
                    "cancellation": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/bulletins/course-cancel",
                        "description": "Course cancellation announcements"
                    },
                    "news": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/bulletins/",
                        "description": "Latest news announcements"
                    },
                    "media": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/series/live-streaming",
                        "description": "Multimedia content and lectures"
                    }
                },
                "chrome_devtools": {
                    "enabled": False,
                    "headless": True,
                    "timeout": 30,
                    "debug_port": 9222,
                    "fallback_to_selenium": True,
                    "description": "Chrome DevTools integration for advanced web scraping"
                },
                "data_sync": {
                    "excel_output_dir": "generated_documents/website_monitoring",
                    "mysql_batch_size": 100,
                    "backup_enabled": True,
                    "cleanup_old_files_days": 30,
                    "excel_enabled": True,
                    "mysql_enabled": False,
                    "description": "Data synchronization to Excel and MySQL"
                },
                "notifications": {
                    "line_enabled": False,
                    "email_enabled": True,
                    "immediate_alerts": ["cancellation"],
                    "daily_summary": ["carousel", "news", "media"],
                    "cycle_notifications": False,
                    "description": "Notification settings for different content types"
                },
                "performance": {
                    "max_concurrent_scrapers": 2,
                    "request_delay_seconds": 2,
                    "retry_attempts": 3,
                    "timeout_seconds": 30,
                    "memory_limit_mb": 512,
                    "log_level": "INFO",
                    "description": "Performance and resource management settings"
                }
            },
            "deployment": {
                "environment": "production",
                "auto_start": False,
                "health_check_enabled": True,
                "health_check_interval": 300,
                "log_retention_days": 30,
                "description": "Deployment and operational settings"
            }
        }
    
    def _create_cli_wrapper_scripts(self):
        """Create CLI wrapper scripts for easy execution"""
        
        # Windows batch script
        batch_script = """@echo off
REM Website Monitoring CLI Wrapper
REM Usage: monitor.bat [command] [options]

cd /d "%~dp0"
python website_monitoring_cli.py %*
"""
        
        batch_path = os.path.join(self.target_dir, 'monitor.bat')
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_script)
        
        # PowerShell script
        ps_script = """# Website Monitoring CLI Wrapper
# Usage: ./monitor.ps1 [command] [options]

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

python website_monitoring_cli.py @args
"""
        
        ps_path = os.path.join(self.target_dir, 'monitor.ps1')
        with open(ps_path, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        self.logger.info("Created CLI wrapper scripts")
    
    def initialize_system(self) -> Tuple[bool, str]:
        """
        Initialize monitoring system after deployment
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            self.logger.info("Initializing monitoring system...")
            
            # Change to target directory
            original_cwd = os.getcwd()
            os.chdir(self.target_dir)
            
            try:
                # Initialize configuration manager
                config_manager = ConfigManager(logger=self.logger)
                
                # Create default monitoring configuration
                if not config_manager.create_default_monitoring_config():
                    return False, "Failed to create default monitoring configuration"
                
                # Initialize monitoring controller
                controller = MonitoringController(logger=self.logger)
                
                # Initialize system
                success, message = controller.initialize_system()
                
                if success:
                    self.logger.info("System initialization completed successfully")
                    return True, "System initialized successfully"
                else:
                    self.logger.error(f"System initialization failed: {message}")
                    return False, f"System initialization failed: {message}"
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            error_msg = f"Error during system initialization: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def run_deployment_tests(self) -> Tuple[bool, List[str]]:
        """
        Run deployment validation tests
        
        Returns:
            Tuple[bool, List[str]]: (all_passed, test_results)
        """
        test_results = []
        all_passed = True
        
        try:
            self.logger.info("Running deployment tests...")
            
            # Change to target directory for tests
            original_cwd = os.getcwd()
            os.chdir(self.target_dir)
            
            try:
                # Test 1: Configuration loading
                try:
                    config_manager = ConfigManager(logger=self.logger)
                    config = config_manager.get_config()
                    test_results.append("✓ Configuration loading test passed")
                except Exception as e:
                    test_results.append(f"✗ Configuration loading test failed: {e}")
                    all_passed = False
                
                # Test 2: Monitoring controller initialization
                try:
                    controller = MonitoringController(logger=self.logger)
                    success, message = controller.initialize_system()
                    if success:
                        test_results.append("✓ Monitoring controller initialization test passed")
                    else:
                        test_results.append(f"✗ Monitoring controller initialization test failed: {message}")
                        all_passed = False
                except Exception as e:
                    test_results.append(f"✗ Monitoring controller test failed: {e}")
                    all_passed = False
                
                # Test 3: CLI interface
                try:
                    from website_monitoring_cli import WebsiteMonitoringCLI
                    cli = WebsiteMonitoringCLI(verbose=False)
                    test_results.append("✓ CLI interface test passed")
                except Exception as e:
                    test_results.append(f"✗ CLI interface test failed: {e}")
                    all_passed = False
                
                # Test 4: Directory structure
                required_dirs = self.deployment_config['required_directories']
                missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
                
                if not missing_dirs:
                    test_results.append("✓ Directory structure test passed")
                else:
                    test_results.append(f"✗ Directory structure test failed: missing {missing_dirs}")
                    all_passed = False
                
                # Test 5: File permissions
                try:
                    test_file = 'deployment_test_permissions.tmp'
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    test_results.append("✓ File permissions test passed")
                except Exception as e:
                    test_results.append(f"✗ File permissions test failed: {e}")
                    all_passed = False
                
            finally:
                os.chdir(original_cwd)
            
            if all_passed:
                self.logger.info("All deployment tests passed")
            else:
                self.logger.error("Some deployment tests failed")
            
            return all_passed, test_results
            
        except Exception as e:
            error_msg = f"Error running deployment tests: {e}"
            self.logger.error(error_msg)
            return False, [f"✗ Test execution error: {e}"]
    
    def create_deployment_report(self, validation_results: Tuple[bool, List[str]], 
                               test_results: Tuple[bool, List[str]]) -> str:
        """
        Create deployment report
        
        Args:
            validation_results: Environment validation results
            test_results: Deployment test results
            
        Returns:
            str: Path to deployment report file
        """
        try:
            report = {
                'deployment_info': {
                    'timestamp': datetime.now().isoformat(),
                    'target_directory': self.target_dir,
                    'python_version': sys.version,
                    'deployer_version': '1.0.0'
                },
                'environment_validation': {
                    'passed': validation_results[0],
                    'errors': validation_results[1] if not validation_results[0] else []
                },
                'deployment_tests': {
                    'passed': test_results[0],
                    'results': test_results[1]
                },
                'deployment_status': 'SUCCESS' if validation_results[0] and test_results[0] else 'FAILED',
                'next_steps': self._get_next_steps(validation_results[0], test_results[0])
            }
            
            report_path = os.path.join(self.target_dir, f'deployment_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Deployment report created: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Error creating deployment report: {e}")
            return ""
    
    def _get_next_steps(self, validation_passed: bool, tests_passed: bool) -> List[str]:
        """
        Get next steps based on deployment results
        
        Args:
            validation_passed: Whether validation passed
            tests_passed: Whether tests passed
            
        Returns:
            List[str]: List of next steps
        """
        if validation_passed and tests_passed:
            return [
                "1. Review and update config.json with your specific settings",
                "2. Configure email settings for notifications",
                "3. Test single monitoring cycle: python website_monitoring_cli.py run",
                "4. Enable desired content types: python website_monitoring_cli.py enable carousel news",
                "5. Start continuous monitoring: python website_monitoring_cli.py start --interval 60",
                "6. Monitor system status: python website_monitoring_cli.py status --detailed"
            ]
        elif validation_passed:
            return [
                "1. Fix deployment test failures before proceeding",
                "2. Check log files for detailed error information",
                "3. Verify all required Python dependencies are installed",
                "4. Re-run deployment tests after fixes"
            ]
        else:
            return [
                "1. Fix environment validation errors",
                "2. Ensure all required files are present",
                "3. Install missing Python dependencies",
                "4. Verify ChromeDriver installation",
                "5. Re-run deployment after fixes"
            ]
    
    def deploy(self) -> Tuple[bool, str]:
        """
        Execute complete deployment process
        
        Returns:
            Tuple[bool, str]: (success, report_path)
        """
        try:
            self.logger.info("Starting website monitoring deployment...")
            
            # Step 1: Validate environment
            validation_results = self.validate_environment()
            if not validation_results[0]:
                self.logger.error("Environment validation failed")
                report_path = self.create_deployment_report(validation_results, (False, []))
                return False, report_path
            
            # Step 2: Setup directory structure
            if not self.setup_directory_structure():
                self.logger.error("Directory structure setup failed")
                return False, ""
            
            # Step 3: Deploy configuration templates
            if not self.deploy_configuration_templates():
                self.logger.error("Configuration template deployment failed")
                return False, ""
            
            # Step 4: Initialize system
            init_success, init_message = self.initialize_system()
            if not init_success:
                self.logger.error(f"System initialization failed: {init_message}")
                return False, ""
            
            # Step 5: Run deployment tests
            test_results = self.run_deployment_tests()
            
            # Step 6: Create deployment report
            report_path = self.create_deployment_report(validation_results, test_results)
            
            success = validation_results[0] and test_results[0]
            
            if success:
                self.logger.info("Website monitoring deployment completed successfully")
            else:
                self.logger.error("Website monitoring deployment completed with errors")
            
            return success, report_path
            
        except Exception as e:
            error_msg = f"Error during deployment: {e}"
            self.logger.error(error_msg)
            return False, ""


def main():
    """
    Main deployment script entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Website Monitoring Deployment Script')
    parser.add_argument(
        '--target-dir', '-t',
        default='.',
        help='Target deployment directory (default: current directory)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        print("Website Monitoring System Deployment")
        print("=" * 40)
        
        # Initialize deployer
        deployer = WebsiteMonitoringDeployer(args.target_dir, logger)
        
        # Execute deployment
        success, report_path = deployer.deploy()
        
        if success:
            print("✓ Deployment completed successfully!")
            if report_path:
                print(f"  Report: {report_path}")
            print("\nNext steps:")
            print("1. Review and update config.json with your settings")
            print("2. Test the system: python website_monitoring_cli.py run")
            print("3. Start monitoring: python website_monitoring_cli.py start")
        else:
            print("✗ Deployment failed!")
            if report_path:
                print(f"  Check report for details: {report_path}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"✗ Deployment error: {e}")
        logger.error(f"Deployment error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())