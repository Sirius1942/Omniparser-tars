import json
import os
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def get_openai_config(self) -> Dict[str, Any]:
        """获取OpenAI配置"""
        openai_config = self.config.get("openai", {})
        
        # 验证必要的配置项
        api_key = openai_config.get("api_key")
        if not api_key or api_key == "your-openai-api-key-here":
            raise ValueError("请在config.json中设置有效的OpenAI API密钥")
        
        return openai_config
    
    def get_caption_config(self) -> Dict[str, Any]:
        """获取图标描述配置"""
        return self.config.get("caption", {})
    
    def get_delays_config(self) -> Dict[str, Any]:
        """获取延迟配置"""
        return self.config.get("delays", {})
    
    def get_openai_api_key(self) -> str:
        """获取OpenAI API密钥"""
        return self.get_openai_config()["api_key"]
    
    def get_openai_base_url(self) -> str:
        """获取OpenAI API基础URL"""
        return self.get_openai_config().get("base_url", "https://api.openai.com/v1")
    
    def get_openai_model(self) -> str:
        """获取OpenAI模型名称"""
        return self.get_openai_config().get("model", "gpt-4o")
    
    def get_default_prompt(self) -> str:
        """获取默认提示词"""
        return self.get_caption_config().get("default_prompt", "请描述这个图标的功能")
    
    def get_batch_size(self) -> int:
        """获取批处理大小"""
        return self.get_openai_config().get("batch_size", 3)
    
    def get_max_tokens(self) -> int:
        """获取最大token数"""
        return self.get_openai_config().get("max_tokens", 50)
    
    def get_temperature(self) -> float:
        """获取温度参数"""
        return self.get_openai_config().get("temperature", 0.1)
    
    def get_request_timeout(self) -> int:
        """获取请求超时时间"""
        return self.get_openai_config().get("request_timeout", 30)
    
    def get_max_retries(self) -> int:
        """获取最大重试次数"""
        return self.get_openai_config().get("max_retries", 3)
    
    def get_request_delay(self) -> float:
        """获取请求间延迟"""
        return self.get_delays_config().get("between_requests", 0.1)
    
    def get_batch_delay(self) -> float:
        """获取批次间延迟"""
        return self.get_delays_config().get("between_batches", 0.5)
    
    def update_config(self, key_path: str, value: Any):
        """
        更新配置项
        
        Args:
            key_path: 配置键路径，如 "openai.api_key"
            value: 新值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 导航到最后一级的父级
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存配置
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    
    def validate_config(self) -> bool:
        """验证配置的完整性"""
        try:
            self.get_openai_config()
            return True
        except ValueError:
            return False

# 全局配置实例
_config_instance = None

def get_config(config_path: str = "config.json") -> Config:
    """获取配置实例（单例模式）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance

def reload_config(config_path: str = "config.json") -> Config:
    """重新加载配置"""
    global _config_instance
    _config_instance = Config(config_path)
    return _config_instance 