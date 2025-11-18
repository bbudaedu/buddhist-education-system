#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 website_monitor.py 中的 NotificationProcessor
"""

# 讀取檔案
with open('ebook/website_monitor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到並替換
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 檢查是否是要替換的行
    if 'self.notification_processor = NotificationProcessor(' in line:
        print(f"找到第 {i+1} 行: {line.strip()}")
        
        # 替換為新的程式碼
        indent = ' ' * 12
        new_lines.append(f"{indent}# Initialize LINE notification service\n")
        new_lines.append(f"{indent}line_service = LineNotificationService(\n")
        new_lines.append(f"{indent}    config=self.config,\n")
        new_lines.append(f"{indent}    logger=self.logger\n")
        new_lines.append(f"{indent})\n")
        new_lines.append(f"{indent}\n")
        new_lines.append(f"{indent}# Initialize UnifiedNotificationService for integrated notifications\n")
        new_lines.append(f"{indent}self.notification_processor = UnifiedNotificationService(\n")
        new_lines.append(f"{indent}    line_service=line_service,\n")
        new_lines.append(f"{indent}    email_sender=self.email_sender,\n")
        new_lines.append(f"{indent}    logger=self.logger\n")
        new_lines.append(f"{indent})\n")
        
        # 跳過舊的程式碼 (包括 config, email_sender, logger, 右括號)
        i += 1
        while i < len(lines) and ')' not in lines[i]:
            i += 1
        i += 1  # 跳過右括號那一行
        
        # 跳過空行
        while i < len(lines) and lines[i].strip() == '':
            i += 1
        
        # 替換 logger.info
        if i < len(lines) and 'Notification components initialized' in lines[i]:
            new_lines.append(f"\n")
            new_lines.append(f"{indent}self.logger.info(\"Unified notification service initialized\")\n")
            i += 1
        
        continue
    
    new_lines.append(line)
    i += 1

# 寫回檔案
with open('ebook/website_monitor.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 修復完成！")
