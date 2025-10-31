# check_json_structure.py
import json
import os

def check_json_structure():
    json_path = "D:\\chatbot_covid19_intern_procodecg\\faiss\\faiss_textcovid19_texts.json"
    
    print(f"🔍 Checking JSON structure: {json_path}")
    
    if not os.path.exists(json_path):
        print("❌ File tidak ditemukan!")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 JSON type: {type(data)}")
    
    if isinstance(data, list):
        print(f"📋 Data is list with {len(data)} items")
        if len(data) > 0:
            print(f"📄 First item type: {type(data[0])}")
            print(f"📄 First item: {data[0]}")
            
            # Check first few items
            for i in range(min(3, len(data))):
                print(f"Item {i}: {type(data[i])} - {str(data[i])[:100]}...")
                
    elif isinstance(data, dict):
        print(f"📋 Data is dict with keys: {list(data.keys())}")
        for key, value in list(data.items())[:3]:
            print(f"Key '{key}': {type(value)} - {str(value)[:100]}...")
    
    else:
        print(f"❓ Unknown data type: {type(data)}")

if __name__ == "__main__":
    check_json_structure()