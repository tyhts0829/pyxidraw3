"""
共通レジストリ基底クラス
shapes/ と effects/ の両方で使用する統一されたレジストリシステム
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Type


class BaseRegistry(ABC):
    """レジストリの基底クラス"""
    
    def __init__(self):
        self._registry: Dict[str, Type] = {}
    
    def register(self, name: str) -> Callable:
        """クラスをレジストリに登録するデコレータ"""
        def decorator(cls: Type) -> Type:
            if name in self._registry:
                raise ValueError(f"'{name}' is already registered")
            self._registry[name] = cls
            return cls
        return decorator
    
    def get(self, name: str) -> Type:
        """登録されたクラスを取得"""
        if name not in self._registry:
            raise KeyError(f"'{name}' is not registered")
        return self._registry[name]
    
    def list_all(self) -> List[str]:
        """登録されているすべての名前を取得"""
        return list(self._registry.keys())
    
    def is_registered(self, name: str) -> bool:
        """指定された名前が登録されているかチェック"""
        return name in self._registry
    
    def unregister(self, name: str) -> None:
        """レジストリから削除"""
        if name in self._registry:
            del self._registry[name]
    
    def clear(self) -> None:
        """レジストリをクリア"""
        self._registry.clear()
    
    @property
    def registry(self) -> Dict[str, Type]:
        """レジストリの読み取り専用アクセス"""
        return self._registry.copy()


class CacheableRegistry(BaseRegistry):
    """キャッシング機能付きレジストリ"""
    
    def __init__(self):
        super().__init__()
        self._instance_cache: Dict[str, Any] = {}
    
    def get_instance(self, name: str, **kwargs) -> Any:
        """インスタンスを取得（キャッシュ機能付き）"""
        cache_key = (name, tuple(sorted(kwargs.items())))
        
        if cache_key not in self._instance_cache:
            cls = self.get(name)
            instance = cls(**kwargs)
            self._instance_cache[cache_key] = instance
        
        return self._instance_cache[cache_key]
    
    def clear_instance_cache(self) -> None:
        """インスタンスキャッシュをクリア"""
        self._instance_cache.clear()