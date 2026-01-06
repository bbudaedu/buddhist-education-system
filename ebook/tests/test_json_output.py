#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test JSON Output Format
測試 JSON 輸出格式
"""

import json
from datetime import datetime
from pathlib import Path


def test_json_serialization():
    """Test that the output summary can be serialized to JSON"""
    
    print("Testing JSON serialization...")
    
    # Simulate monitoring statistics
    stats = {
        'cycles_completed': 1,
        'total_content_processed': 9,
        'errors_encountered': 0,
        'last_successful_cycle': datetime.now(),
        'average_cycle_time': 383.70
    }
    
    # Create output summary (same format as run_daily_monitoring.py)
    output_summary = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "execution_time_seconds": 383.70,
        "statistics": {
            "cycles_completed": stats.get('cycles_completed', 0),
            "total_content_processed": stats.get('total_content_processed', 0),
            "errors_encountered": stats.get('errors_encountered', 0),
            "last_successful_cycle": stats.get('last_successful_cycle').isoformat() if stats.get('last_successful_cycle') else None,
            "average_cycle_time": stats.get('average_cycle_time', 0)
        },
        "message": "Monitoring cycle completed successfully"
    }
    
    # Try to serialize to JSON
    try:
        json_str = json.dumps(output_summary, ensure_ascii=False, indent=2)
        print("✅ JSON serialization successful!")
        print("\nOutput:")
        print(json_str)
        
        # Try to write to file
        output_dir = Path("generated_documents")
        output_dir.mkdir(exist_ok=True)
        
        test_file = output_dir / "test_output.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(output_summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Successfully wrote to: {test_file}")
        
        # Read it back to verify
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print("✅ Successfully read back from file")
        print(f"\nLoaded data keys: {list(loaded_data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False


if __name__ == "__main__":
    success = test_json_serialization()
    exit(0 if success else 1)
