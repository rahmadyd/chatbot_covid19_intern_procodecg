# main.py (di root folder)
import os
import sys

# Tambahkan path src ke sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test semua import berhasil"""
    try:
        from src.retriever import Retriever
        print("✅ Berhasil import Retriever")
        
        from src.generation import generate_answer
        print("✅ Berhasil import generate_answer")
        
        from src.guard_rail import GuardRail
        print("✅ Berhasil import GuardRail")
        
        import src.config as config
        print("✅ Berhasil import config")
        
        print("\n🎉 Semua import berhasil!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error lain: {e}")
        return False

if __name__ == "__main__":
    test_imports()