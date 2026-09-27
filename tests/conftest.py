"""
Pytest configuration and environment fixtures.
Ensures repository root is always on sys.path.
"""

import os
import sys

# Prevent OpenBLAS memory allocation failures on systems with low paging commit limits
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

# Ensure repository root is on sys.path for test discovery
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
