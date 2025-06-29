"""
エフェクトレジストリ - @effectデコレータの実装
仕様書に記載されている@effectデコレータを提供。
"""

from typing import Dict, Type, Callable, Any
from .base import BaseEffect


# グローバルエフェクトレジストリ
_effect_registry: Dict[str, Type[BaseEffect]] = {}


def effect(name: str):
    """エフェクトをレジストリに登録するデコレータ。
    
    仕様書に記載されている@effectデコレータの実装。
    effects/*.pyでエフェクトクラスを登録するために使用。
    
    Usage:
        @effect("noise")
        class Noise(BaseEffect):
            ...
    
    Args:
        name: エフェクト名
        
    Returns:
        デコレータ関数
    """
    def decorator(effect_class: Type[BaseEffect]):
        _effect_registry[name] = effect_class
        return effect_class
    return decorator


def get_effect(name: str) -> Type[BaseEffect]:
    """登録されたエフェクトクラスを取得。
    
    Args:
        name: エフェクト名
        
    Returns:
        エフェクトクラス
        
    Raises:
        KeyError: エフェクトが登録されていない場合
    """
    if name not in _effect_registry:
        raise KeyError(f"Effect '{name}' is not registered")
    return _effect_registry[name]


def list_effects() -> list[str]:
    """登録されているエフェクトの一覧を取得。
    
    Returns:
        エフェクト名のリスト
    """
    return list(_effect_registry.keys())


def clear_registry():
    """レジストリをクリア（テスト用）。"""
    _effect_registry.clear()