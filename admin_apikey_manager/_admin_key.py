import secrets
import math
import time
from enum import Enum, auto
from typing import Optional, Union, Any
from pathlib import Path
from loguru import logger
import environs

import threading
import asyncio

class AdminKeySource(Enum):
    """API Key 来源枚举"""
    ENV = "ENV"                                 # 来自环境变量
    FILE = "FILE"                               # 来自文件
    RANDOM = "RANDOM"                           # 随机生成
    CUSTOM = "CUSTOM"                           # 手动设置
    AUTOMATIC_ROTATION = "AUTOMATIC_ROTATION"   # 自动轮换

class AdminKeyManager:
    """
    管理 Admin API Key 的类，支持从环境变量、文件、随机生成或手动设置。
    """
    def __init__(
        self,
        env: Optional[environs.Env] = None,
        api_key: Optional[str] = None,
        auto_generate_prefix: str = "adk-",
        min_key_length: int = 16,
        min_key_different_characters: int = 6,
        min_entropy: float = 3.5
    ):
        """
        初始化 AdminKeyManager 实例。

        :param env: Env 对象，用于获取环境变量。
        :param api_key: 初始 API Key。
        :raise ValueError: API Key 长度不足 16 字符
        :raise ValueError: API Key 中包含少于 6 种字符
        :raise ValueError: API Key 熵不足
        """
        self._env = env or environs.Env()

        self._auto_generate_prefix = auto_generate_prefix
        self._min_key_length = min_key_length
        self._min_key_different_characters = min_key_different_characters
        self._min_entropy = min_entropy
        
        if api_key:
            self._api_key: Optional[str] = self._examine_api_key(api_key)
            self._source: Optional[AdminKeySource] = AdminKeySource.CUSTOM
        else:
            self._api_key: Optional[str] = None
            self._source: Optional[AdminKeySource] = None
            self._load_key()

        self._automatic_rotation_thread: Optional[threading.Thread] = None
        self._automatic_rotation_thread_stop_event = threading.Event()
        self._automatic_rotation_coroutine: Optional[asyncio.Task] = None

    def __eq__(self, other: Any) -> bool:
        """
        允许直接比较 API Key：
        - key_manager == "your-key"  # 比较字符串
        - key_manager == other_manager  # 比较两个 Manager 的 Key
        """
        if self._api_key is None:
            return False

        if isinstance(other, str):
            return self.validate_key(other)
        elif isinstance(other, AdminKeyManager):
            return self.validate_key(other.api_key)
        return False

    def __repr__(self) -> str:
        """
        返回 Key 的模糊化表示（避免日志泄露完整 Key）
        """
        if not self._api_key:
            return "<AdminKeyManager: UNINITIALIZED>"
        return f"<AdminKeyManager: {self._api_key[:2]}...{self._api_key[-2:]}(from {self.source.value})>"

    @property
    def source(self) -> AdminKeySource:
        """
        返回当前 API Key 的来源

        :raise ValueError: Key 未初始化
        :return: 来源
        """
        if self._source is None:
            raise ValueError("API Key Not Initialized")
        return self._source

    @property
    def api_key(self) -> str:
        """
        返回当前的 API Key

        :raise ValueError: Key 未初始化
        :return: API Key
        """
        if self._api_key is None:
            raise ValueError("API Key Not Initialized")
        return self._api_key
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        """
        设置 API Key

        :param value: API Key
        """
        self._api_key = self._examine_api_key(value)
        self._source = AdminKeySource.CUSTOM

    def _load_key(self) -> None:
        """
        尝试从环境变量加载 Key，否则生成随机 Key
        """
        try:
            api_key = self._env.str("ADMIN_API_KEY")
            source = AdminKeySource.ENV
            logger.info("API Key Loaded from Environment Variables", user_id="[System]")
        except environs.EnvError:
            api_key = self._generate_an_api_key()
            source = AdminKeySource.RANDOM
            logger.warning(f"API Key Not Found in Environment Variables, Generated Randomly(Only for Development): {api_key}", user_id="[System]")
        
        self._api_key = self._examine_api_key(api_key)
        self._source = source
    
    def generate(self) -> None:
        """
        生成新的随机 API Key
        """
        self._api_key = self._generate_an_api_key()
        self._source = AdminKeySource.RANDOM

    def _generate_an_api_key(self) -> str:
        """
        生成新的随机 API Key

        :return: API Key
        """
        return self._examine_api_key(f"{self._auto_generate_prefix}{secrets.token_urlsafe(32)}")

    def set_custom_key(self, key: str) -> None:
        """
        手动设置 API Key

        :param key: API Key
        :raise ValueError: API Key 不能为空
        """
        if not key:
            raise ValueError("API Key must not be empty")
        self._api_key = self._examine_api_key(key)
        self._source = AdminKeySource.CUSTOM
        logger.info("API Key Set Manually", user_id="[System]")

    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """
        从文件加载 API Key（同步）

        :param file_path: 文件路径
        :raise FileNotFoundError: 文件不存在
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        self._api_key = self._examine_api_key(path.read_text().strip())
        self._source = AdminKeySource.FILE
        logger.info(f"API Key Loaded from File: {path}", user_id="[System]")

    def save_to_file(self, file_path: Union[str, Path], auto_create_dir: bool = True) -> None:
        """
        保存 API Key 到文件（同步）

        :param file_path: 文件路径
        :param auto_create_dir: 如果文件所在目录不存在，是否自动创建
        :raise FileNotFoundError: 文件所在目录不存在
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True) if auto_create_dir else None

        if not path.parent.exists():
            raise FileNotFoundError(f"Directory not found: {path.parent}")
        
        path.write_text(self._api_key)
        logger.info(f"API Key Saved to File: {path}", user_id="[System]")

    async def load_from_file_async(self, file_path: Union[str, Path]) -> None:
        """
        从文件加载 API Key（异步）

        :param file_path: 文件路径
        :raise FileNotFoundError: 文件不存在
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        import aiofiles
        async with aiofiles.open(path, "r") as f:
            self._api_key = self._examine_api_key((await f.read()).strip())
            self._source = AdminKeySource.FILE
            logger.info(f"API Key Loaded from File: {path}", user_id="[System]")

    async def save_to_file_async(self, file_path: Union[str, Path], auto_create_dir: bool = True) -> None:
        """
        保存 API Key 到文件（异步）

        :param file_path: 文件路径
        :param auto_create_dir: 是否自动创建目录
        :raise FileNotFoundError: 文件所在目录不存在
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True) if auto_create_dir else None

        if not path.parent.exists():
            raise FileNotFoundError(f"Directory not found: {path.parent}")

        import aiofiles
        async with aiofiles.open(path, "w") as f:
            await f.write(self._api_key)
        logger.info(f"Saved API Key to file: {path}", user_id="[System]")

    def validate_key(self, input_key: str) -> bool:
        """
        验证传入的 Key 是否匹配（安全比较，防止时序攻击）

        :param input_key: 传入的 Key
        :raise ValueError: API Key 未设置
        :return: 是否匹配
        """
        if not self._api_key:
            raise ValueError("API Key not set")
        return secrets.compare_digest(input_key, self._api_key)

    # 保证 API Key 安全
    def _examine_api_key(self, api_key: str) -> str:
        """
        检查 API Key 是否符合要求

        :param api_key: 待检查的 API Key
        :raise ValueError: API Key 长度不足 16 字符
        :raise ValueError: API Key 中包含少于 6 种字符
        :raise ValueError: API Key 熵不足
        :return: 检查后的 API Key
        """
        if len(api_key) < self._min_key_length:
            raise ValueError("API Key Length must be at least 16 characters")
        if len(set(api_key)) < self._min_key_different_characters:
            raise ValueError("API Key must contain at least 6 different characters")
        if self._calculate_entropy(api_key) < self._min_entropy:
            raise ValueError("API Key entropy is insufficient")
        return api_key
    
    @staticmethod
    def _calculate_entropy(s: str) -> float:
        """计算字符串的 Shannon 熵（衡量随机性）"""
        freq = {}
        for c in s:
            freq[c] = freq.get(c, 0) + 1
        prob = [f / len(s) for f in freq.values()]
        return -sum(p * math.log2(p) for p in prob)
    
    def _automatic_rotation(self, interval: float):
        """
        自动轮换 API Key

        :param interval: 轮换间隔时间（秒）
        """
        while True:
            if not self._automatic_rotation_thread_stop_event.wait(timeout=interval):
                self._api_key = self._examine_api_key(secrets.token_urlsafe(32))
                self._source = AdminKeySource.AUTOMATIC_ROTATION
            else:
                self._automatic_rotation_thread_stop_event.clear()
                break
    
    async def _automatic_rotation_async(self, interval: float):
        """
        异步自动轮换 API Key

        :param interval: 轮换间隔时间（秒）
        """
        while True:
            try:
                await asyncio.sleep(interval)
                self._api_key = self._examine_api_key(secrets.token_urlsafe(32))
                self._source = AdminKeySource.AUTOMATIC_ROTATION
            except asyncio.CancelledError:
                break
    
    def automatic_rotation(self, interval: float):
        """
        自动轮换 API Key

        :param interval: 轮换间隔 (秒)
        """
        if not self._automatic_rotation_thread.is_alive():
            self._automatic_rotation_thread = threading.Thread(
                target=self._automatic_rotation, args=(interval,)
            )
            self._automatic_rotation_thread.start()

    async def automatic_rotation_async(self, interval: float):
        """
        异步自动轮换 API Key

        :param interval: 轮换间隔 (秒)
        """
        if self._automatic_rotation_coroutine.done():
            self._automatic_rotation_coroutine = asyncio.create_task(
                self._automatic_rotation_async(interval)
            )
    
    def stop_automatic_rotation(self):
        """
        停止自动轮换 API Key
        """
        if self._automatic_rotation_thread and self._automatic_rotation_thread.is_alive():
            self._automatic_rotation_thread_stop_event.set()
    
    async def stop_automatic_rotation_async(self):
        """
        停止自动轮换 API Key
        """
        if self._automatic_rotation_coroutine and not self._automatic_rotation_coroutine.done():
            self._automatic_rotation_coroutine.cancel()