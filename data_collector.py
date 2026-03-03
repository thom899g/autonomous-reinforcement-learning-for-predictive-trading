"""
Robust market data collector with error handling and Firebase persistence.
Handles rate limiting, connection drops, and data validation.
"""
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

class MarketDataCollector:
    """Collects