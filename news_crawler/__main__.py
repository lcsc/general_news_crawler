

from __future__ import annotations

import sys
import time

if __name__ == "__main__":
    from .cli.application import main
    start = time.time()
    res = main()
    end = time.time() 
    print("Execution time: ",end - start) 
    sys.exit(res)