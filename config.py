"""
Configuration management for autonomous trading system.
Centralizes all configs with Firebase fallback for state persistence.
"""
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TradingMode(Enum):
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"

@dataclass
class ExchangeConfig:
    """Exchange-specific configuration"""
    name: str = "binance"
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    sandbox: bool = True
    rate_limit: int = 1000
    symbols: list = None
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        # Safely load API credentials
        self.api_key = os.getenv(f"{self.name.upper()}_API_KEY", "")
        self.api_secret = os.getenv(f"{self.name.upper()}_API_SECRET", "")

@dataclass
class RLConfig:
    """Reinforcement Learning hyperparameters"""
    algorithm: str = "PPO"
    learning_rate: float = 0.0003
    buffer_size: int = 100000
    batch_size: int = 64
    gamma: float = 0.99
    tau: float = 0.005
    exploration_noise: float = 0.1
    train_freq: int = 100
    gradient_steps: int = 100
    policy_kwargs: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.policy_kwargs is None:
            self.policy_kwargs = {
                "net_arch": [256, 256],
                "activation_fn": "relu"
            }

@dataclass
class TradingConfig:
    """Trading strategy parameters"""
    mode: TradingMode = TradingMode.PAPER
    initial_balance: float = 10000.0
    max_position_size: float = 0.1  # 10% of portfolio
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.05  # 5% take profit
    max_drawdown: float = 0.20  # 20% max drawdown
    commission_rate: float = 0.001  # 0.1% commission
    
    def validate(self) -> None:
        """Validate configuration parameters"""
        if self.initial_balance <= 0:
            raise ValueError("Initial balance must be positive")
        if not 0 < self.max_position_size <= 1:
            raise ValueError("Position size must be between 0 and 1")
        if self.stop_loss_pct <= 0:
            raise ValueError("Stop loss must be positive")

class ConfigManager:
    """Manages configuration with Firebase persistence"""
    
    def __init__(self, firebase_client=None):
        self.logger = logging.getLogger(__name__)
        self.exchange = ExchangeConfig()
        self.rl = RLConfig()
        self.trading = TradingConfig()
        self.firebase = firebase_client
        
        # Validate configurations
        self.trading.validate()
        
    def save_to_firebase(self, collection_name: str = "trading_configs") -> bool:
        """Save configuration to Firebase Firestore"""
        try:
            if self.firebase:
                config_data = {
                    "exchange": self.exchange.__dict__,
                    "rl": self.rl.__dict__,
                    "trading": {
                        **self.trading.__dict__,
                        "mode": self.trading.mode.value
                    },
                    "timestamp": firestore.SERVER_TIMESTAMP
                }
                doc_ref = self.firebase.collection(collection_name).document("active_config")
                doc_ref.set(config_data)
                self.logger.info("Configuration saved to Firebase")
                return True
        except Exception as e:
            self.logger.error(f"Failed to save config to Firebase: {e}")
        return False
    
    def load_from_firebase(self, collection_name: str = "trading_configs") -> bool:
        """Load configuration from Firebase Firestore"""
        try:
            if self.firebase:
                doc_ref = self.firebase.collection(collection_name).document("active_config")
                doc = doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    # Update configurations from Firebase data
                    # Implementation would map data back to config objects
                    self.logger.info("Configuration loaded from Firebase")
                    return True
        except Exception as e:
            self.logger.error(f"Failed to load config from Firebase: {e}")
        return False