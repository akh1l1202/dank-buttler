import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure the src directory is in the Python search path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    # Load environment variables first
    load_dotenv()
    
    from dank_butler.bot import run_bot
    run_bot()

if __name__ == "__main__":
    main()
