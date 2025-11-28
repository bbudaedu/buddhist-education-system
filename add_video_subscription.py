#!/usr/bin/env python3
"""
Add video subscription handling to webhookHandler.ts at line 248
"""

def add_video_subscription():
    file_path = r"d:\AIstudio\newinfo\Line-bot-llm-mysql\src\handlers\webhookHandler.ts"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the insertion point: after line 247 (after the closing brace of "訂閱新書")
    # We'll insert before line 248 (the blank line)
    insert_index = 248  # This is the blank line after "訂閱新書"
    
    # Prepare the lines to insert
    new_lines = [
        '      // 訂閱影音通知（支援模糊匹配）\n',
        '      if (message.includes(\'訂閱\') && (message.includes(\'影音\') || message.includes(\'視訊\') || message.includes(\'影片\') || message.includes(\'最新影音\'))) {\n',
        '        // 暫時使用臨時回應，未來可添加專門的 videos 類型\n',
        '        await lineMessagingService.sendTextMessage(replyToken, \'感謝您的訂閱！目前影音通知功能正在開發中，請先訂閱「新書通知」來接收最新法寶資訊。\');\n',
        '        return true;\n',
        '      }\n',
        '\n',  # Blank line to match the code style
    ]
    
    # Insert the new lines at the specified position
    lines[insert_index:insert_index] = new_lines
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Successfully inserted video subscription handling at line {insert_index + 1}")
    print(f"   Added {len(new_lines)} lines")
    return True

if __name__ == '__main__':
    try:
        add_video_subscription()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
