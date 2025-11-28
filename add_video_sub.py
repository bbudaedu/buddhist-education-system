#!/usr/bin/env python3
"""
Add video subscription handling to webhookHandler.ts at line 248
"""

def add_video_subscription():
    file_path = r"d:\AIstudio\newinfo\Line-bot-llm-mysql\src\handlers\webhookHandler.ts"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Insert at line 248 (index 247, after line 247's "}")
    insert_index = 248
    
    # Prepare the lines to insert (after the blank line at 248)
    new_lines = [
        r'      // 訂閱影音通知（支援模糊匹配）' + '\n',
        r'      if (message.includes(\'訂閱\') && (message.includes(\'影音\') || message.includes(\'視訊\') || message.includes(\'影片\') || message.includes(\'最新影音\'))) {' + '\n',
        r'        // 暫時使用臨時回應，未來可添加專門的 videos 類型' + '\n',
        r'        await lineMessagingService.sendTextMessage(replyToken, \'感謝您的訂閱！目前影音通知功能正在開發中，請先訂閱「新書通知」來接收最新法寶資訊。\');' + '\n',
        r'        return true;' + '\n',
        r'      }' + '\n',
        r'' + '\n',  # Blank line to match the surrounding code style
    ]
    
    # Insert the new lines at position 248 (which is the blank line, we insert before it)
    lines[insert_index:insert_index] = new_lines
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Successfully inserted video subscription handling at line {insert_index + 1}")
    return True

if __name__ == '__main__':
    add_video_subscription()
