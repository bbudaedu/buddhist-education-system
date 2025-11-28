#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick syntax checker for Python files
"""
import sys
import py_compile

def check_syntax(file_path):
    """Check if Python file has valid syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"✓ Syntax check passed: {file_path}")
        return True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error in {file_path}:")
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick syntax checker for Python files
"""
import sys
import py_compile

def check_syntax(file_path):
    """Check if Python file has valid syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"✓ Syntax check passed: {file_path}")
        return True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error in {file_path}:")
        print(f"  Line {e.exc_value.lineno}: {e.exc_value.msg}")
        print(f"  {e.exc_value.text}")
        return False

if __name__ == "__main__":
    files_to_check = [
        r"d:\AIstudio\newinfo\ebook\database_sync.py",
        r"d:\AIstudio\newinfo\ebook\website_monitor.py",
        r"d:\AIstudio\newinfo\ebook\line_notification_service.py",
        r"d:\AIstudio\newinfo\ebook\book_scraper.py"
    ]

    has_error = False
    for file_path in files_to_check:
        if not check_syntax(file_path):
            has_error = True

    if has_error:
        sys.exit(1)
    else:
        sys.exit(0)
