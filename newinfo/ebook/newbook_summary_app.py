#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新書摘要與郵件發送系統
Buddhist Education New Book Summary and Email Distribution System

This application monitors the Budaedu.org website for new books, downloads PDFs,
generates AI-powered summaries using Google Gemini Pro 2.5, and distributes them via email.
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import logging
import json
import os
from datetime import datetime
import threading
import queue

# Application version
VERSION = "1.0.0"

# Configuration file path
CONFIG_FILE = "config.json"

# Default configuration template
DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "chromedriver_path": "chromedriver-win64\\chromedriver.exe",
    "target_url": "https://www.budaedu.org",
    "baseline_book_title": "",
    "download_dir": "downloads",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "",
    "smtp_password": "",
    "email_recipients": "jackyfang@budaedu.org,tyguo@budaedu.org",
    "last_run_date": ""
}


class TkinterLogHandler(logging.Handler):
    """Custom logging handler for Tkinter ScrolledText widget with thread-safe message insertion"""
    
    def __init__(self, text_widget):
        """
        Initialize TkinterLogHandler
        
        Args:
            text_widget: Tkinter ScrolledText widget for displaying log messages
        """
        super().__init__()
        self.text_widget = text_widget
        self.message_queue = queue.Queue()
        
        # Start the UI update loop
        self._schedule_update()
    
    def emit(self, record):
        """
        Emit a log record (called by logging system)
        
        Args:
            record: LogRecord instance
        """
        try:
            msg = self.format(record)
            # Add message to queue for thread-safe processing
            self.message_queue.put(msg)
        except Exception:
            self.handleError(record)
    
    def _schedule_update(self):
        """Schedule the next UI update check"""
        self._process_queue()
        # Schedule next check in 100ms
        if self.text_widget.winfo_exists():
            self.text_widget.after(100, self._schedule_update)
    
    def _process_queue(self):
        """Process all pending log messages from the queue"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                self._insert_message(msg)
        except queue.Empty:
            pass
    
    def _insert_message(self, msg):
        """
        Insert message into text widget (must be called from main thread)
        
        Args:
            msg: Formatted log message string
        """
        try:
            if self.text_widget.winfo_exists():
                # Enable editing temporarily
                self.text_widget.config(state='normal')
                
                # Insert message at the end
                self.text_widget.insert(tk.END, msg + '\n')
                
                # Auto-scroll to the latest message
                self.text_widget.see(tk.END)
                
                # Disable editing to make it read-only
                self.text_widget.config(state='disabled')
        except Exception:
            pass


class ConfigManager:
    """Manages application configuration with JSON-based persistence"""
    
    def __init__(self, config_file=CONFIG_FILE, logger=None):
        """
        Initialize ConfigManager
        
        Args:
            config_file: Path to the configuration file
            logger: Logger instance for logging operations
        """
        self.config_file = config_file
        self.logger = logger
        self.config = {}
    
    def load(self):
        """
        Load configuration from JSON file
        
        Returns:
            dict: Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                if self.logger:
                    self.logger.info(f"已載入設定檔: {self.config_file}")
                
                # Merge with defaults to ensure all keys exist
                for key, value in DEFAULT_CONFIG.items():
                    if key not in self.config:
                        self.config[key] = value
                
                return self.config
            except json.JSONDecodeError as e:
                if self.logger:
                    self.logger.error(f"設定檔格式錯誤: {e}")
                self.config = DEFAULT_CONFIG.copy()
                return self.config
            except Exception as e:
                if self.logger:
                    self.logger.error(f"載入設定檔失敗: {e}")
                self.config = DEFAULT_CONFIG.copy()
                return self.config
        else:
            if self.logger:
                self.logger.info("設定檔不存在，使用預設設定")
            self.config = DEFAULT_CONFIG.copy()
            return self.config
    
    def save(self, config=None):
        """
        Save configuration to JSON file
        
        Args:
            config: Configuration dictionary to save (uses self.config if None)
        
        Returns:
            bool: True if save successful, False otherwise
        """
        if config is not None:
            self.config = config
        
        try:
            # Use atomic write with temporary file
            temp_file = self.config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            # Replace original file
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            os.rename(temp_file, self.config_file)
            
            if self.logger:
                self.logger.info(f"已儲存設定檔: {self.config_file}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"儲存設定檔失敗: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False
    
    def get(self, key, default=None):
        """
        Get configuration value by key
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def validate_api_key(self):
        """
        Validate Gemini API key
        
        Returns:
            tuple: (is_valid, error_message)
        """
        api_key = self.config.get('gemini_api_key', '')
        if not api_key or api_key.strip() == '':
            return False, "Gemini API Key 未設定"
        return True, ""
    
    def validate_chromedriver_path(self):
        """
        Validate ChromeDriver executable path
        
        Returns:
            tuple: (is_valid, error_message)
        """
        path = self.config.get('chromedriver_path', '')
        if not path or path.strip() == '':
            return False, "ChromeDriver 路徑未設定"
        if not os.path.exists(path):
            return False, f"ChromeDriver 檔案不存在: {path}"
        if not os.path.isfile(path):
            return False, f"ChromeDriver 路徑不是檔案: {path}"
        return True, ""
    
    def validate_smtp_settings(self):
        """
        Validate SMTP email settings
        
        Returns:
            tuple: (is_valid, error_message)
        """
        smtp_server = self.config.get('smtp_server', '')
        smtp_port = self.config.get('smtp_port', 0)
        smtp_username = self.config.get('smtp_username', '')
        smtp_password = self.config.get('smtp_password', '')
        
        if not smtp_server or smtp_server.strip() == '':
            return False, "SMTP 伺服器未設定"
        if not smtp_port or smtp_port <= 0:
            return False, "SMTP 連接埠無效"
        if not smtp_username or smtp_username.strip() == '':
            return False, "SMTP 使用者名稱未設定"
        if not smtp_password or smtp_password.strip() == '':
            return False, "SMTP 密碼未設定"
        
        return True, ""
    
    def validate_download_dir(self):
        """
        Validate download directory path
        
        Returns:
            tuple: (is_valid, error_message)
        """
        path = self.config.get('download_dir', '')
        if not path or path.strip() == '':
            return False, "下載目錄未設定"
        
        # Create directory if it doesn't exist
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                if self.logger:
                    self.logger.info(f"已建立下載目錄: {path}")
            except Exception as e:
                return False, f"無法建立下載目錄: {e}"
        
        if not os.path.isdir(path):
            return False, f"下載路徑不是目錄: {path}"
        
        return True, ""
    
    def validate_all(self):
        """
        Validate all configuration settings
        
        Returns:
            tuple: (is_valid, list_of_error_messages)
        """
        errors = []
        
        is_valid, error = self.validate_api_key()
        if not is_valid:
            errors.append(error)
        
        is_valid, error = self.validate_chromedriver_path()
        if not is_valid:
            errors.append(error)
        
        is_valid, error = self.validate_smtp_settings()
        if not is_valid:
            errors.append(error)
        
        is_valid, error = self.validate_download_dir()
        if not is_valid:
            errors.append(error)
        
        return len(errors) == 0, errors


class NewBookSummaryApp:
    """Main application class for the New Book Summary and Email System"""
    
    def __init__(self, master):
        self.master = master
        self.master.title(f"新書摘要與郵件發送系統 v{VERSION}")
        self.master.geometry("900x700")
        
        # Application state
        self.config_manager = None
        self.is_processing = False
        self.stop_flag = False
        self.logger = None
        self.log_text_widget = None
        
        # UI variables (initialize before create_widgets)
        self.api_key_var = None
        self.chromedriver_var = None
        self.target_url_var = None
        self.baseline_title_var = None
        self.download_dir_var = None
        self.smtp_server_var = None
        self.smtp_port_var = None
        self.smtp_username_var = None
        self.smtp_password_var = None
        self.email_recipients_var = None
        self.status_var = None
        self.progress_var = None
        
        # UI widgets
        self.api_key_entry = None
        self.chromedriver_entry = None
        self.chromedriver_browse_btn = None
        self.target_url_entry = None
        self.baseline_title_entry = None
        self.download_dir_entry = None
        self.download_dir_browse_btn = None
        self.smtp_server_entry = None
        self.smtp_port_entry = None
        self.smtp_username_entry = None
        self.smtp_password_entry = None
        self.email_recipients_entry = None
        self.start_btn = None
        self.stop_btn = None
        self.check_btn = None
        self.status_label = None
        self.progress_label = None
        
        # Initialize UI
        self.create_widgets()
        self.setup_logging()
        
        # Load configuration on startup
        self.load_config()
        
        # Set up window close handler for configuration persistence
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle window close event with enhanced configuration persistence"""
        try:
            # Always save configuration before closing
            self.save_config()
            
            if not self.is_processing:
                self.logger.info("應用程式正常關閉")
                self.master.destroy()
            else:
                # Ask user if they want to stop processing and close
                if messagebox.askokcancel("確認關閉", "處理正在進行中。確定要停止並關閉應用程式嗎？"):
                    self.stop_flag = True
                    
                    # Stop the main processor if it exists
                    if hasattr(self, 'main_processor') and self.main_processor:
                        self.main_processor.request_stop()
                        
                        # Wait a short time for graceful shutdown
                        self.logger.info("等待處理安全停止...")
                        if self.main_processor.wait_for_completion(timeout=5.0):
                            self.logger.info("處理已安全停止")
                        else:
                            self.logger.warning("處理停止超時，強制關閉")
                    
                    self.logger.info("應用程式關閉 (處理已中斷)")
                    self.master.destroy()
        except Exception as e:
            self.logger.error(f"關閉應用程式時發生錯誤: {e}")
            # Force close even if there's an error
            self.master.destroy()
        
    def create_widgets(self):
        """Create all UI components"""
        # Main container with padding
        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Configuration Panel =====
        config_frame = tk.LabelFrame(main_frame, text="系統設定", padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Gemini API Key
        row = 0
        tk.Label(config_frame, text="Gemini API Key:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = tk.Entry(config_frame, textvariable=self.api_key_var, width=50, show='*')
        self.api_key_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(0, 5))
        
        # ChromeDriver Path
        row += 1
        tk.Label(config_frame, text="ChromeDriver 路徑:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.chromedriver_var = tk.StringVar()
        self.chromedriver_entry = tk.Entry(config_frame, textvariable=self.chromedriver_var, width=50)
        self.chromedriver_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(0, 5))
        self.chromedriver_browse_btn = tk.Button(config_frame, text="瀏覽...", command=self.browse_chromedriver)
        self.chromedriver_browse_btn.grid(row=row, column=2, pady=5)
        
        # Target URL
        row += 1
        tk.Label(config_frame, text="目標網站 URL:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.target_url_var = tk.StringVar()
        self.target_url_entry = tk.Entry(config_frame, textvariable=self.target_url_var, width=50)
        self.target_url_entry.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        # Baseline Book Title
        row += 1
        tk.Label(config_frame, text="基準書籍標題:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.baseline_title_var = tk.StringVar()
        self.baseline_title_entry = tk.Entry(config_frame, textvariable=self.baseline_title_var, width=50)
        self.baseline_title_entry.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        # Download Directory
        row += 1
        tk.Label(config_frame, text="下載目錄:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.download_dir_var = tk.StringVar()
        self.download_dir_entry = tk.Entry(config_frame, textvariable=self.download_dir_var, width=50)
        self.download_dir_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(0, 5))
        self.download_dir_browse_btn = tk.Button(config_frame, text="瀏覽...", command=self.browse_download_dir)
        self.download_dir_browse_btn.grid(row=row, column=2, pady=5)
        
        # SMTP Server
        row += 1
        tk.Label(config_frame, text="SMTP 伺服器:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.smtp_server_var = tk.StringVar()
        self.smtp_server_entry = tk.Entry(config_frame, textvariable=self.smtp_server_var, width=30)
        self.smtp_server_entry.grid(row=row, column=1, sticky='w', pady=5)
        
        # SMTP Port
        tk.Label(config_frame, text="連接埠:", anchor='w').grid(row=row, column=1, sticky='e', pady=5, padx=(0, 5))
        self.smtp_port_var = tk.StringVar()
        self.smtp_port_entry = tk.Entry(config_frame, textvariable=self.smtp_port_var, width=10)
        self.smtp_port_entry.grid(row=row, column=2, sticky='w', pady=5)
        
        # SMTP Username
        row += 1
        tk.Label(config_frame, text="SMTP 使用者名稱:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.smtp_username_var = tk.StringVar()
        self.smtp_username_entry = tk.Entry(config_frame, textvariable=self.smtp_username_var, width=50)
        self.smtp_username_entry.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        # SMTP Password
        row += 1
        tk.Label(config_frame, text="SMTP 密碼:", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.smtp_password_var = tk.StringVar()
        self.smtp_password_entry = tk.Entry(config_frame, textvariable=self.smtp_password_var, width=50, show='*')
        self.smtp_password_entry.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        # Email Recipients
        row += 1
        tk.Label(config_frame, text="收件人 (逗號分隔):", width=20, anchor='w').grid(row=row, column=0, sticky='w', pady=5)
        self.email_recipients_var = tk.StringVar()
        self.email_recipients_entry = tk.Entry(config_frame, textvariable=self.email_recipients_var, width=50)
        self.email_recipients_entry.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        # Configure grid column weights for resizing
        config_frame.columnconfigure(1, weight=1)
        
        # ===== Control Panel =====
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(control_frame)
        buttons_frame.pack(side=tk.LEFT)
        
        # Start Processing Button
        self.start_btn = tk.Button(
            buttons_frame,
            text="開始處理",
            command=self.start_processing,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop Processing Button
        self.stop_btn = tk.Button(
            buttons_frame,
            text="停止處理",
            command=self.stop_processing,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Check Configuration Button
        self.check_btn = tk.Button(
            buttons_frame,
            text="檢查設定",
            command=self.check_configuration,
            bg='#2196F3',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        self.check_btn.pack(side=tk.LEFT)
        
        # Status display frame
        status_frame = tk.Frame(control_frame)
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Current status label
        tk.Label(status_frame, text="狀態:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(20, 5))
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        self.status_label = tk.Label(
            status_frame, 
            textvariable=self.status_var,
            font=('Arial', 9),
            fg='#2E7D32',
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress information label
        self.progress_var = tk.StringVar()
        self.progress_var.set("")
        self.progress_label = tk.Label(
            status_frame,
            textvariable=self.progress_var,
            font=('Arial', 8),
            fg='#666666',
            anchor='e'
        )
        self.progress_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # ===== Log Display Panel =====
        log_frame = tk.LabelFrame(main_frame, text="執行日誌", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # ScrolledText widget for log display
        self.log_text_widget = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=100,
            height=20,
            state='disabled',
            font=('Consolas', 9)
        )
        self.log_text_widget.pack(fill=tk.BOTH, expand=True)
    
    def setup_logging(self):
        """Set up logging system with file and UI handlers"""
        # Create logger
        self.logger = logging.getLogger('NewBookSummaryApp')
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_filename = f'log_{timestamp}.txt'
        
        # Create file handler with UTF-8 encoding
        try:
            file_handler = logging.FileHandler(
                log_filename,
                mode='w',
                encoding='utf-8-sig'  # UTF-8 with BOM for Chinese characters
            )
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            
            # Add file handler to logger
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"無法建立日誌檔案: {e}")
        
        # Create Tkinter UI handler (if log widget exists)
        if self.log_text_widget:
            ui_handler = TkinterLogHandler(self.log_text_widget)
            ui_handler.setLevel(logging.INFO)
            
            # Create formatter for UI (simpler format)
            ui_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            )
            ui_handler.setFormatter(ui_formatter)
            
            # Add UI handler to logger
            self.logger.addHandler(ui_handler)
        
        # Log startup message
        self.logger.info("=" * 60)
        self.logger.info(f"新書摘要與郵件發送系統 v{VERSION} 已啟動")
        self.logger.info(f"日誌檔案: {log_filename}")
        self.logger.info("=" * 60)
    
    def load_config(self):
        """Load configuration from config.json"""
        # Initialize ConfigManager with logger
        self.config_manager = ConfigManager(CONFIG_FILE, self.logger)
        config = self.config_manager.load()
        
        # Populate UI fields with loaded configuration
        self.api_key_var.set(config.get('gemini_api_key', ''))
        self.chromedriver_var.set(config.get('chromedriver_path', ''))
        self.target_url_var.set(config.get('target_url', ''))
        self.baseline_title_var.set(config.get('baseline_book_title', ''))
        self.download_dir_var.set(config.get('download_dir', ''))
        self.smtp_server_var.set(config.get('smtp_server', ''))
        self.smtp_port_var.set(str(config.get('smtp_port', 587)))
        self.smtp_username_var.set(config.get('smtp_username', ''))
        self.smtp_password_var.set(config.get('smtp_password', ''))
        self.email_recipients_var.set(config.get('email_recipients', ''))
    
    def save_config(self):
        """Save configuration to config.json"""
        if self.config_manager:
            # Update config from UI fields
            self.config_manager.set('gemini_api_key', self.api_key_var.get())
            self.config_manager.set('chromedriver_path', self.chromedriver_var.get())
            self.config_manager.set('target_url', self.target_url_var.get())
            self.config_manager.set('baseline_book_title', self.baseline_title_var.get())
            self.config_manager.set('download_dir', self.download_dir_var.get())
            self.config_manager.set('smtp_server', self.smtp_server_var.get())
            
            # Convert port to integer
            try:
                port = int(self.smtp_port_var.get())
                self.config_manager.set('smtp_port', port)
            except ValueError:
                self.config_manager.set('smtp_port', 587)
            
            self.config_manager.set('smtp_username', self.smtp_username_var.get())
            self.config_manager.set('smtp_password', self.smtp_password_var.get())
            self.config_manager.set('email_recipients', self.email_recipients_var.get())
            
            # Save to file
            self.config_manager.save()
    
    def browse_chromedriver(self):
        """Open file dialog to select ChromeDriver executable"""
        filename = filedialog.askopenfilename(
            title="選擇 ChromeDriver 執行檔",
            filetypes=[("執行檔", "*.exe"), ("所有檔案", "*.*")]
        )
        if filename:
            self.chromedriver_var.set(filename)
    
    def browse_download_dir(self):
        """Open directory dialog to select download directory"""
        dirname = filedialog.askdirectory(
            title="選擇下載目錄"
        )
        if dirname:
            self.download_dir_var.set(dirname)
    
    def disable_buttons(self):
        """Disable control buttons during processing"""
        self.start_btn.config(state='disabled')
        self.check_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        # Disable configuration inputs
        self.api_key_entry.config(state='disabled')
        self.chromedriver_entry.config(state='disabled')
        self.chromedriver_browse_btn.config(state='disabled')
        self.target_url_entry.config(state='disabled')
        self.baseline_title_entry.config(state='disabled')
        self.download_dir_entry.config(state='disabled')
        self.download_dir_browse_btn.config(state='disabled')
        self.smtp_server_entry.config(state='disabled')
        self.smtp_port_entry.config(state='disabled')
        self.smtp_username_entry.config(state='disabled')
        self.smtp_password_entry.config(state='disabled')
        self.email_recipients_entry.config(state='disabled')
        
        # Update status display
        self._update_status_display("準備中...", "正在啟動處理", "#FF9800")
    
    def enable_buttons(self):
        """Enable control buttons after processing"""
        self.start_btn.config(state='normal')
        self.check_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        # Enable configuration inputs
        self.api_key_entry.config(state='normal')
        self.chromedriver_entry.config(state='normal')
        self.chromedriver_browse_btn.config(state='normal')
        self.target_url_entry.config(state='normal')
        self.baseline_title_entry.config(state='normal')
        self.download_dir_entry.config(state='normal')
        self.download_dir_browse_btn.config(state='normal')
        self.smtp_server_entry.config(state='normal')
        self.smtp_port_entry.config(state='normal')
        self.smtp_username_entry.config(state='normal')
        self.smtp_password_entry.config(state='normal')
        self.email_recipients_entry.config(state='normal')
        
        # Update status display
        self._update_status_display("就緒", "", "#2E7D32")
    
    def start_processing(self):
        """Start the main processing workflow"""
        self.logger.info("開始處理...")
        
        # Save current configuration
        self.save_config()
        
        # Validate configuration before starting
        is_valid, errors = self.config_manager.validate_all()
        if not is_valid:
            error_message = "設定驗證失敗，無法開始處理：\n\n"
            for error in errors:
                error_message += f"• {error}\n"
            messagebox.showerror("設定錯誤", error_message)
            return
        
        # Disable buttons during processing
        self.disable_buttons()
        self.is_processing = True
        self.stop_flag = False
        
        try:
            # Import MainProcessor
            from main_processor import MainProcessor
            
            # Create configuration dictionary for MainProcessor
            config = {
                'gemini_api_key': self.api_key_var.get(),
                'chromedriver_path': self.chromedriver_var.get(),
                'target_url': self.target_url_var.get(),
                'baseline_book_title': self.baseline_title_var.get(),
                'download_dir': self.download_dir_var.get(),
                'smtp_server': self.smtp_server_var.get(),
                'smtp_port': int(self.smtp_port_var.get()) if self.smtp_port_var.get().isdigit() else 587,
                'smtp_username': self.smtp_username_var.get(),
                'smtp_password': self.smtp_password_var.get(),
                'email_recipients': self.email_recipients_var.get()
            }
            
            # Initialize MainProcessor with shared logger for consistent logging across all modules
            self.main_processor = MainProcessor(config, self.logger)
            
            # Set status callback for UI updates
            self.main_processor.set_status_callback(self._on_processing_status_update)
            
            # Start processing in background thread
            success = self.main_processor.start_processing_async()
            
            if success:
                self.logger.info("背景處理已啟動")
                self._update_status("背景處理已啟動...")
            else:
                self.logger.error("啟動背景處理失敗")
                self.enable_buttons()
                self.is_processing = False
                messagebox.showerror("啟動失敗", "無法啟動背景處理，請檢查日誌了解詳細錯誤。")
                
        except Exception as e:
            self.logger.error(f"啟動處理時發生錯誤: {e}")
            self.enable_buttons()
            self.is_processing = False
            messagebox.showerror("啟動錯誤", f"啟動處理時發生錯誤：\n{e}")
    
    def _on_processing_status_update(self, message: str):
        """
        Handle status updates from MainProcessor (called from worker thread)
        
        Args:
            message: Status message from MainProcessor
        """
        # Schedule UI update in main thread (thread-safe)
        self.master.after(0, self._update_ui_status, message)
    
    def _update_status(self, message: str):
        """
        Update status with a simple message (for compatibility with MainProcessor)
        
        Args:
            message: Status message to display
        """
        self._update_status_display(message, "", "#2196F3")
    
    def _update_status_display(self, status_text: str, progress_text: str = "", status_color: str = "#2E7D32"):
        """
        Update status and progress display in UI
        
        Args:
            status_text: Main status text to display
            progress_text: Progress information text
            status_color: Color for status text
        """
        try:
            if self.status_var:
                self.status_var.set(status_text)
            if self.status_label:
                self.status_label.config(fg=status_color)
            if self.progress_var:
                self.progress_var.set(progress_text)
        except Exception as e:
            self.logger.warning(f"更新狀態顯示失敗: {e}")
    
    def _update_ui_status(self, message: str):
        """
        Update UI status (called in main thread)
        
        Args:
            message: Status message to display
        """
        # Log the status update
        self.logger.info(f"[狀態更新] {message}")
        
        # Update status display based on message content
        if "載入進度快取" in message:
            self._update_status_display("載入進度中...", "", "#FF9800")
        elif "初始化系統模組" in message:
            self._update_status_display("初始化模組中...", "", "#FF9800")
        elif "搜尋新書" in message:
            self._update_status_display("搜尋新書中...", "", "#FF9800")
        elif "開始處理" in message and "本新書" in message:
            # Extract book count from message like "開始處理 5 本新書..."
            import re
            match = re.search(r'開始處理 (\d+) 本新書', message)
            if match:
                book_count = match.group(1)
                self._update_status_display("處理書籍中...", f"共 {book_count} 本書", "#2196F3")
            else:
                self._update_status_display("處理書籍中...", "", "#2196F3")
        elif "處理書籍" in message and "/" in message:
            # Extract progress from message like "處理書籍 3/10..."
            import re
            match = re.search(r'處理書籍 (\d+)/(\d+)', message)
            if match:
                current, total = match.groups()
                progress_text = f"進度: {current}/{total}"
                percentage = int(current) / int(total) * 100
                self._update_status_display("處理書籍中...", f"{progress_text} ({percentage:.0f}%)", "#2196F3")
            else:
                self._update_status_display("處理書籍中...", "", "#2196F3")
        elif "生成文件" in message:
            self._update_status_display("生成文件中...", "", "#FF9800")
        elif "發送郵件" in message:
            self._update_status_display("發送郵件中...", "", "#FF9800")
        elif "處理完成" in message or "成功完成" in message:
            self._update_status_display("處理完成", "所有任務已完成", "#4CAF50")
        elif "中斷" in message or "停止" in message:
            self._update_status_display("已停止", "處理已中斷", "#FF5722")
        elif "錯誤" in message or "失敗" in message:
            self._update_status_display("錯誤", "處理發生錯誤", "#F44336")
        elif "未成功完成" in message:
            self._update_status_display("部分完成", "處理未完全成功", "#FF9800")
        elif "背景處理已啟動" in message:
            self._update_status_display("執行中...", "背景處理已啟動", "#2196F3")
        elif "沒有找到新書" in message:
            self._update_status_display("無新書", "沒有找到新書", "#4CAF50")
        else:
            # Default status update
            self._update_status_display("執行中...", "", "#2196F3")
        
        # Check if processing has completed
        if hasattr(self, 'main_processor') and self.main_processor:
            if not self.main_processor.is_running:
                # Processing has finished, re-enable buttons
                self.enable_buttons()
                self.is_processing = False
                
                # Show completion message based on status
                if "完成" in message or "成功完成" in message:
                    messagebox.showinfo("處理完成", "新書摘要處理已完成！請查看日誌了解詳細結果。")
                elif "中斷" in message or "停止" in message:
                    messagebox.showwarning("處理中斷", "處理已被中斷。進度已儲存，可重新啟動繼續處理。")
                elif "錯誤" in message or "失敗" in message:
                    messagebox.showerror("處理錯誤", "處理過程中發生錯誤。請查看日誌了解詳細錯誤資訊。")
                elif "未成功完成" in message:
                    messagebox.showwarning("處理未完全成功", "處理過程中遇到一些問題，但部分書籍可能已成功處理。請查看日誌了解詳細情況。")
                elif "沒有找到新書" in message:
                    messagebox.showinfo("無新書", "目前沒有找到新書需要處理。")
    
    def stop_processing(self):
        """Stop the current processing task"""
        if self.is_processing and hasattr(self, 'main_processor') and self.main_processor:
            self.logger.warning("正在停止處理...")
            self.stop_flag = True
            
            # Request MainProcessor to stop gracefully
            self.main_processor.request_stop()
            
            # Update UI to show stopping status
            self.logger.info("已發送停止請求，等待處理安全停止...")
        else:
            self.logger.info("沒有正在執行的處理可停止")
    
    def check_configuration(self):
        """Validate system configuration with enhanced user feedback"""
        self.logger.info("開始檢查設定...")
        self._update_status_display("檢查設定中...", "", "#FF9800")
        
        # Save current configuration from UI
        self.save_config()
        
        # Validate all settings
        is_valid, errors = self.config_manager.validate_all()
        
        if is_valid:
            self.logger.info("✓ 所有設定檢查通過")
            self._update_status_display("設定正確", "所有設定檢查通過", "#4CAF50")
            messagebox.showinfo(
                "設定檢查",
                "✓ 所有設定檢查通過！\n\n系統已準備就緒，可以開始處理新書。"
            )
            # Reset to ready status after a short delay
            self.master.after(3000, lambda: self._update_status_display("就緒", "", "#2E7D32"))
        else:
            self.logger.error("✗ 設定檢查失敗")
            self._update_status_display("設定錯誤", f"發現 {len(errors)} 個問題", "#F44336")
            
            error_message = "發現以下設定問題：\n\n"
            for i, error in enumerate(errors, 1):
                error_message += f"{i}. {error}\n"
                self.logger.error(f"  - {error}")
            
            error_message += "\n請修正這些問題後再開始處理。"
            
            messagebox.showerror(
                "設定檢查失敗",
                error_message
            )
            # Keep error status until user fixes issues


def main():
    """Application entry point"""
    root = tk.Tk()
    app = NewBookSummaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
