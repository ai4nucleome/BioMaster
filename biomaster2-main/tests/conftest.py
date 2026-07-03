from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".opencode" / "runtime"

if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))
