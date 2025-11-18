# -*- coding: utf-8 -*-

# ====================================================================================
# 佛學講座字幕校對工具 (本機桌面版) v3.1
#
# 更新日誌：
# - 移除行數不符時的錯誤標記填充功能。
# - 現在程式會完整返回 Gemini API 的原始輸出，即使行數與輸入不一致。
#
# 使用前請先安裝必要的函式庫:
# pip install google-generativeai pandas openpyxl pypdf
# ====================================================================================

import os
import json
import logging
import re
import time
import threading
import datetime
import pypdf
import google.generativeai as genai

# --- GUI 相關函式庫 ---
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import font as tkFont

# ====================================================================================
# 核心處理邏輯 (後端)
# ====================================================================================

CONFIG_FILE = 'config.json'
GEMINI_API_BATCH_MAX_LINES = 6000
DEFAULT_GEMINI_MAIN_INSTRUCTION = (
    "# 角色 你是一位精通佛學經論的專家，特別專精於大般涅槃經，同時你也是一位嚴謹、專業的逐字稿校對員。\n"
    "任務背景 你的任務是校對一段由 Whisper 自動語音辨識系統產生的講座字幕文本。這段文很多近音字錯誤、同音字錯誤，你必須依據我提供的【上課講義原文】及【你的佛學知識】作為正確標準，來修正 Whisper 文本中的聽打錯誤。\n"
    "嚴格依照以下規則，直接修正錯誤："
)
DEFAULT_GEMINI_CORRECTION_RULES = (
    "校對規則：\n"
    "    1. 這是講座字幕的文本。請逐行處理提供的「字幕文本」。\n"
    "    2. **你的輸出絕對必須不多不少，正好是 {batch_line_count} 行。這是最重要的規則，絕不允許任何合併或拆分行。**\n"
    "    3. 輸出結果的總行數必須與輸入的總行數完全相同。\n"
    "    4. 如果某一行不需要修改，請直接輸出原始該行內容。\n"
    "    5. 根據「上課講義內容」修正「字幕文本」中的任何聽打錯誤或不準確之處。\n"
    "    6. 不要加標點符號。\n"
    "    7. 輸出繁體中文。"
)

def extract_text_from_handouts_dir(logger_instance, handouts_dir):
    full_text = []
    if not os.path.isdir(handouts_dir):
        logger_instance.error(f"講義資料夾 '{handouts_dir}' 不存在。")
        return None
    
    supported_files = [f for f in os.listdir(handouts_dir) if f.lower().endswith(('.pdf', '.md'))]
    if not supported_files:
        logger_instance.warning(f"資料夾 '{handouts_dir}' 中沒有找到任何 .pdf 或 .md 檔案。")
        return None

    logger_instance.info(f"正在從資料夾 '{handouts_dir}' 中的 {len(supported_files)} 個講義檔案提取文本...")
    for file_name in sorted(supported_files):
        file_path = os.path.join(handouts_dir, file_name)
        try:
            if file_name.lower().endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            full_text.append(page_text)
            elif file_name.lower().endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    full_text.append(file.read())
            logger_instance.info(f"  - 成功提取 '{file_name}'。")
        except Exception as e:
            logger_instance.error(f"  - 從 '{file_name}' 提取文本時發生錯誤: {e}", exc_info=True)
            
    combined_text = "\n\n".join(full_text)
    if combined_text:
        logger_instance.info(f"所有講義提取完成，共 {len(combined_text)} 字元文本。")
    else:
        logger_instance.warning("未能從任何講義檔案提取到文本。")
    return combined_text

def load_gemini_processed_state(logger_instance, state_file_path):
    try:
        if os.path.exists(state_file_path):
            with open(state_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data if isinstance(data, list) else [])
        logger_instance.info(f"Gemini 狀態檔案 '{state_file_path}' 未找到。將創建新的。")
    except json.JSONDecodeError:
        logger_instance.warning(f"解碼 Gemini 狀態檔案 '{state_file_path}' 時發生錯誤。將重新處理。")
    except Exception as e:
        logger_instance.error(f"載入 Gemini 狀態檔案 '{state_file_path}' 時發生錯誤: {e}。", exc_info=True)
    return set()

def save_gemini_processed_state(logger_instance, state_file_path, processed_items_set):
    temp_state_file_path = state_file_path + ".tmp"
    try:
        os.makedirs(os.path.dirname(state_file_path), exist_ok=True)
        with open(temp_state_file_path, 'w', encoding='utf-8') as f:
            json.dump(list(processed_items_set), f, ensure_ascii=False, indent=4)
        os.replace(temp_state_file_path, state_file_path)
        logger_instance.debug(f"Gemini 處理狀態已成功儲存至 '{state_file_path}'。")
    except Exception as e:
        logger_instance.error(f"儲存 Gemini 處理狀態至 '{state_file_path}' 時發生錯誤: {e}", exc_info=True)
        if os.path.exists(temp_state_file_path):
            try: os.remove(temp_state_file_path)
            except OSError as oe: logger_instance.error(f"移除臨時 Gemini 狀態檔案 '{temp_state_file_path}' 時發生錯誤: {oe}", exc_info=True)

def get_gemini_correction(logger_instance, api_key, transcribed_text_lines, pdf_context, main_instruction, correction_rules, start_batch_idx=0):
    try:
        if not api_key:
            logger_instance.critical("錯誤: Gemini API Key 未提供。")
            return
        genai.configure(api_key=api_key)
    except Exception as e:
        logger_instance.error(f"配置 Gemini SDK 時出錯: {e}", exc_info=True)
        return
    actual_model_name = "gemini-2.5-pro"
    logger_instance.info(f"Gemini API 將使用模型: {actual_model_name}")
    model = genai.GenerativeModel(model_name=actual_model_name,generation_config={"temperature": 1, "top_p": 0.95, "top_k": 40, "response_mime_type": "text/plain"})
    total_lines = len(transcribed_text_lines)
    num_batches = (total_lines + GEMINI_API_BATCH_MAX_LINES - 1) // GEMINI_API_BATCH_MAX_LINES
    if start_batch_idx > 0:
        logger_instance.info(f"將從第 {start_batch_idx + 1}/{num_batches} 個批次繼續處理。")
    for batch_idx in range(start_batch_idx, num_batches):
        start_index = batch_idx * GEMINI_API_BATCH_MAX_LINES
        end_index = min((batch_idx + 1) * GEMINI_API_BATCH_MAX_LINES, total_lines)
        current_batch_lines = transcribed_text_lines[start_index:end_index]
        if not current_batch_lines: continue
        logger_instance.info(f"正在處理第 {batch_idx+1}/{num_batches} 批次的文本 (行 {start_index+1} 到 {end_index})...")
        max_retries = 5
        for attempt in range(max_retries):
            try:
                batch_text = "\n".join(current_batch_lines)
                batch_rules = correction_rules.format(batch_line_count=len(current_batch_lines))
                full_prompt = (f"{main_instruction}\n\n上課講義內容：\n---\n{pdf_context}\n---\n\n"
                               f"以下是需要校對的字幕文本 (共 {len(current_batch_lines)} 行):\n---\n{batch_text}\n---\n\n{batch_rules}")
                response = model.generate_content(full_prompt, request_options={"timeout": 900})
                
                # --- *** 核心修正點 *** ---
                corrected_text = response.text
                raw_lines = corrected_text.strip().split('\n')
                
                # 檢查行數不符並記錄警告，但不再修改輸出
                if len(raw_lines) != len(current_batch_lines):
                    logger_instance.warning(f"Gemini (批次 {batch_idx+1}) 返回行數 ({len(raw_lines)}) 與原始行數 ({len(current_batch_lines)}) 不一致。將直接使用返回的內容。")
                
                # 直接使用 Gemini 的原始返回行
                corrected_lines_for_this_batch = raw_lines
                # -------------------------

                yield batch_idx, corrected_lines_for_this_batch
                break
            except Exception as e:
                logger_instance.error(f"調用 Gemini API (批次 {batch_idx+1}, 嘗試 {attempt+1}/{max_retries}) 時發生錯誤: {e}")
                if attempt < max_retries - 1:
                    time.sleep(30)
                else:
                    raise e
        else:
             logger_instance.critical(f"批次 {batch_idx+1} 經過 {max_retries} 次嘗試後仍然失敗，終止此項目的處理。")
             return

def process_transcriptions_and_apply_gemini(logger_instance, api_key, pdf_context_text, main_instruction, correction_rules, batch_root_dir, target_project_name=None):
    if not pdf_context_text:
        logger_instance.error("講義文本尚未載入。請先執行步驟三。")
        return
    
    GEMINI_STATE_FILE_PATH = os.path.join(batch_root_dir, ".gemini_processed_state.json")
    gemini_processed_items = load_gemini_processed_state(logger_instance, GEMINI_STATE_FILE_PATH)
    logger_instance.info(f"已載入 {len(gemini_processed_items)} 個已完成的項目記錄。")
    
    subdirs_or_paths = []
    if target_project_name:
        logger_instance.info(f"--- 進入單一測試模式，目標: {target_project_name} ---")
        if not os.path.isdir(target_project_name):
            logger_instance.error(f"錯誤：找不到指定的測試項目資料夾: {target_project_name}")
            return
        subdirs_or_paths = [target_project_name]
    else:
        logger_instance.info(f"--- 進入批次處理模式，掃描目錄: {batch_root_dir} ---")
        if not os.path.isdir(batch_root_dir):
            logger_instance.error(f"轉錄輸入目錄 '{batch_root_dir}' 未找到。")
            return
        subdirs_or_paths = [d for d in os.listdir(batch_root_dir) if os.path.isdir(os.path.join(batch_root_dir, d))]
    if not subdirs_or_paths:
        logger_instance.info("找不到任何項目進行處理。")
        return

    processed_item_count = 0
    for item_identifier in subdirs_or_paths:
        if os.path.isabs(item_identifier):
            item_path = item_identifier
            base_name = os.path.basename(item_path)
        else:
            item_path = os.path.join(batch_root_dir, item_identifier)
            base_name = item_identifier
        logger_instance.info(f"--- 開始處理項目: {base_name} (位於: {item_path}) ---")
        if not target_project_name and base_name in gemini_processed_items:
            logger_instance.info(f"項目 '{base_name}' 已標記為完成，跳過。")
            continue
        normal_text_path = os.path.join(item_path, f"{base_name}_normal.txt")
        cache_path = os.path.join(item_path, f".{base_name}_progress_cache.json")
        try:
            with open(normal_text_path, 'r', encoding='utf-8') as f: whisper_lines = f.read().splitlines()
            gemini_lines = []
            start_batch = 0
            if os.path.exists(cache_path):
                logger_instance.info(f"發現進度快取檔案，正在載入進度: {cache_path}")
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        gemini_lines = json.load(f)
                    start_batch = len(gemini_lines) // GEMINI_API_BATCH_MAX_LINES
                    logger_instance.info(f"已成功載入 {len(gemini_lines)} 行已完成的校對文本。")
                except Exception as e:
                    logger_instance.warning(f"讀取快取檔案失敗: {e}。將從頭開始。")
                    gemini_lines, start_batch = [], 0
            all_batches_successful = True
            if len(gemini_lines) < len(whisper_lines):
                if target_project_name: logger_instance.info(f"測試模式：強制對 '{base_name}' 進行 Gemini API 校對...")
                try:
                    num_batches = (len(whisper_lines) + GEMINI_API_BATCH_MAX_LINES - 1) // GEMINI_API_BATCH_MAX_LINES
                    gemini_generator = get_gemini_correction(
                        logger_instance, api_key, whisper_lines, pdf_context_text,
                        main_instruction, correction_rules, start_batch_idx=start_batch
                    )
                    for completed_batch_idx, new_lines in gemini_generator:
                        gemini_lines.extend(new_lines)
                        with open(cache_path, 'w', encoding='utf-8') as f:
                            json.dump(gemini_lines, f, ensure_ascii=False)
                        logger_instance.info(f"[進度] 已儲存：完成批次 {completed_batch_idx + 1}/{num_batches}")
                except Exception as e:
                    logger_instance.error(f"'{base_name}' 的 Gemini 校對過程中斷。部分進度已儲存。錯誤: {e}", exc_info=True)
                    all_batches_successful = False
            else:
                logger_instance.info(f"'{base_name}' 的所有校對文本已在快取中，跳過 API 調用。")
            if all_batches_successful:
                logger_instance.info("所有批次處理完成，正在生成最終結果檔案...")
                output_txt_path = os.path.join(item_path, "gemini.txt")
                with open(output_txt_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(gemini_lines))
                logger_instance.info(f"[成功] 成功將校對結果儲存至 {output_txt_path}")
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                    logger_instance.info("已刪除臨時進度快取檔案。")
                if not target_project_name:
                    gemini_processed_items.add(base_name)
                    save_gemini_processed_state(logger_instance, GEMINI_STATE_FILE_PATH, gemini_processed_items)
                logger_instance.info(f"[完成] 項目 {base_name} 處理完成。")
                processed_item_count += 1
            else:
                 logger_instance.warning(f"[中斷] 項目 {base_name} 處理中斷。")
        except FileNotFoundError as e_fnf:
             logger_instance.error(f"處理項目 '{base_name}' 時找不到必要檔案: {e_fnf}。請檢查檔案是否存在。")
             continue
        except Exception as e_main_ops:
            logger_instance.error(f"處理項目 '{base_name}' 時發生主流程錯誤: {e_main_ops}", exc_info=True)
            continue
    logger_instance.info(f"==== 本次運行總共處理了 {processed_item_count} 個項目。流程結束。====")

# ====================================================================================
# 圖形化使用者介面 (前端)
# ====================================================================================
class TkinterLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    def emit(self, record):
        msg = self.format(record)
        def append_message():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)
        self.text_widget.after(0, append_message)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("佛學講座字幕校對工具 v3.1 (原始輸出版)")
        self.master.geometry("850x850")
        self.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.pdf_context_text = ""
        self.create_widgets()
        self.setup_logging()
        self.load_config()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        api_frame = tk.LabelFrame(self, text="步驟一：設定 API 金鑰", padx=5, pady=5)
        api_frame.pack(fill='x', expand=False, pady=5)
        tk.Label(api_frame, text="Gemini API Key:").pack(side='left', padx=(0, 5))
        self.api_key_entry = tk.Entry(api_frame, width=70, show="*")
        self.api_key_entry.pack(side='left', fill='x', expand=True)
        prompt_frame = tk.LabelFrame(self, text="步驟二：設定 Gemini 提示詞", padx=5, pady=5)
        prompt_frame.pack(fill='x', expand=False, pady=5)
        tk.Label(prompt_frame, text="主要指令:").pack(anchor='w')
        self.main_instruction_text = scrolledtext.ScrolledText(prompt_frame, height=6, wrap=tk.WORD)
        self.main_instruction_text.pack(fill='x', expand=True, pady=(0, 5))
        self.main_instruction_text.insert(tk.END, DEFAULT_GEMINI_MAIN_INSTRUCTION)
        tk.Label(prompt_frame, text="校對規則:").pack(anchor='w')
        self.correction_rules_text = scrolledtext.ScrolledText(prompt_frame, height=8, wrap=tk.WORD)
        self.correction_rules_text.pack(fill='x', expand=True)
        self.correction_rules_text.insert(tk.END, DEFAULT_GEMINI_CORRECTION_RULES)
        pdf_frame = tk.LabelFrame(self, text="步驟三：載入講義 (pdf, md)", padx=5, pady=5)
        pdf_frame.pack(fill='x', expand=False, pady=5)
        tk.Label(pdf_frame, text="講義資料夾路徑:").pack(side='left', padx=(0, 5))
        self.pdf_dir_entry = tk.Entry(pdf_frame)
        self.pdf_dir_entry.pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(pdf_frame, text="瀏覽...", command=lambda: self.browse_directory(self.pdf_dir_entry)).pack(side='left')
        self.load_pdf_button = tk.Button(pdf_frame, text="讀取講義文本", command=self.start_pdf_loading)
        self.load_pdf_button.pack(side='left', padx=5)
        batch_frame = tk.LabelFrame(self, text="步驟四：批次處理 (全部)", padx=5, pady=5)
        batch_frame.pack(fill='x', expand=False, pady=5)
        tk.Label(batch_frame, text="批次處理根目錄:").pack(side='left', padx=(0, 5))
        self.batch_dir_entry = tk.Entry(batch_frame)
        self.batch_dir_entry.pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(batch_frame, text="瀏覽...", command=lambda: self.browse_directory(self.batch_dir_entry)).pack(side='left')
        self.run_batch_button = tk.Button(batch_frame, text="開始批次處理", command=self.start_batch_processing, bg="#d4edda")
        self.run_batch_button.pack(side='left', padx=5)
        test_frame = tk.LabelFrame(self, text="步驟五：單獨測試模式", padx=5, pady=5)
        test_frame.pack(fill='x', expand=False, pady=5)
        tk.Label(test_frame, text="測試項目路徑:").pack(side='left', padx=(0, 5))
        self.test_dir_entry = tk.Entry(test_frame)
        self.test_dir_entry.pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(test_frame, text="瀏覽...", command=lambda: self.browse_directory(self.test_dir_entry)).pack(side='left')
        self.run_test_button = tk.Button(test_frame, text="執行單一測試", command=self.start_single_test, bg="#fff3cd")
        self.run_test_button.pack(side='left', padx=5)
        log_frame = tk.LabelFrame(self, text="執行狀態日誌", padx=5, pady=5)
        log_frame.pack(fill='both', expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=10)
        self.log_text.pack(fill='both', expand=True)

    def setup_logging(self):
        self.logger = logging.getLogger('LocalProcessorLogger')
        self.logger.setLevel(logging.INFO)
        if self.logger.hasHandlers(): self.logger.handlers.clear()
        log_filename = f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8-sig')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        ui_handler = TkinterLogHandler(self.log_text)
        ui_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        ui_handler.setFormatter(ui_formatter)
        self.logger.addHandler(ui_handler)
        self.logger.info("應用程式啟動。")
        self.logger.info(f"本此運行的日誌將被儲存到: {log_filename}")

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.api_key_entry.insert(0, config.get('api_key', ''))
                self.pdf_dir_entry.insert(0, config.get('pdf_dir', ''))
                self.batch_dir_entry.insert(0, config.get('batch_dir', ''))
                self.test_dir_entry.insert(0, config.get('test_dir', ''))
                self.logger.info(f"已從 {CONFIG_FILE} 載入上次的設定。")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"讀取設定檔 {CONFIG_FILE} 失敗: {e}。將使用空白設定。")

    def save_config(self):
        config = {
            'api_key': self.api_key_entry.get().strip(),
            'pdf_dir': self.pdf_dir_entry.get().strip(),
            'batch_dir': self.batch_dir_entry.get().strip(),
            'test_dir': self.test_dir_entry.get().strip(),
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        self.logger.info(f"設定已儲存至 {CONFIG_FILE}。")

    def on_closing(self):
        self.save_config()
        self.master.destroy()

    def browse_directory(self, entry_widget):
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def start_pdf_loading(self):
        pdf_dir = self.pdf_dir_entry.get().strip()
        if not pdf_dir:
            messagebox.showerror("錯誤", "請先選擇講義資料夾路徑！")
            return
        self.disable_buttons()
        threading.Thread(target=self.load_pdf_task, args=(pdf_dir,)).start()

    def load_pdf_task(self, pdf_dir):
        self.logger.info("--- 開始讀取講義文本 ---")
        self.pdf_context_text = extract_text_from_handouts_dir(self.logger, pdf_dir) or ""
        if self.pdf_context_text:
            self.logger.info("[成功] 成功讀取並載入講義文本。")
        else:
            self.logger.warning("[警告] 未能從指定資料夾的講義中提取任何文本。")
        self.logger.info("--- 步驟三完成 ---")
        self.enable_buttons()

    def run_process(self, batch_dir, main_instruction, correction_rules, test_dir=None):
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("錯誤", "請先輸入您的 Gemini API Key！")
            self.enable_buttons()
            return
        try:
            process_transcriptions_and_apply_gemini(self.logger, api_key, self.pdf_context_text, main_instruction, correction_rules, batch_dir, test_dir)
        except Exception as e:
            self.logger.error(f"發生未捕獲的頂層錯誤: {e}", exc_info=True)
        finally:
            self.enable_buttons()

    def disable_buttons(self):
        self.load_pdf_button.config(state='disabled')
        self.run_batch_button.config(state='disabled')
        self.run_test_button.config(state='disabled')

    def enable_buttons(self):
        self.load_pdf_button.config(state='normal')
        self.run_batch_button.config(state='normal')
        self.run_test_button.config(state='normal')

    def start_batch_processing(self):
        batch_dir = self.batch_dir_entry.get().strip()
        main_instruction = self.main_instruction_text.get("1.0", tk.END).strip()
        correction_rules = self.correction_rules_text.get("1.0", tk.END).strip()
        if not batch_dir or not main_instruction or not correction_rules:
            messagebox.showerror("錯誤", "請確保批次處理根目錄與提示詞皆已填寫！")
            return
        self.disable_buttons()
        threading.Thread(target=self.run_process, args=(batch_dir, main_instruction, correction_rules)).start()

    def start_single_test(self):
        batch_dir = self.batch_dir_entry.get().strip()
        test_dir = self.test_dir_entry.get().strip()
        main_instruction = self.main_instruction_text.get("1.0", tk.END).strip()
        correction_rules = self.correction_rules_text.get("1.0", tk.END).strip()
        if not batch_dir or not test_dir or not main_instruction or not correction_rules:
            messagebox.showerror("錯誤", "請確保所有路徑與提示詞皆已填寫！")
            return
        self.disable_buttons()
        threading.Thread(target=self.run_process, args=(batch_dir, main_instruction, correction_rules, test_dir)).start()

# --- 程式主入口 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()