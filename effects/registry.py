"""
エフェクトレジストリ - 統一されたレジストリシステム
shapes/と対称性を保った@effectデコレータの実装
"""

from typing import Dict, Type, Callable, Any
from .base import BaseEffect
from common.base_registry import BaseRegistry


# 統一されたレジストリシステム
_effect_registry = BaseRegistry()


def effect(name: str):
    """エフェクトをレジストリに登録するデコレータ。
    
    統一されたレジストリシステムを使用した@effectデコレータ。
    shapes/の@register_shapeと対称性を保った実装。
    
    Usage:
        @effect("noise")
        class Noise(BaseEffect):
            ...
    
    Args:
        name: エフェクト名
        
    Returns:
        デコレータ関数
    """
    return _effect_registry.register(name)


def get_effect(name: str) -> Type[BaseEffect]:
    """登録されたエフェクトクラスを取得。
    
    Args:
        name: エフェクト名
        
    Returns:
        エフェクトクラス
        
    Raises:
        KeyError: エフェクトが登録されていない場合
    """
    return _effect_registry.get(name)


def list_effects() -> list[str]:
    """登録されているエフェクトの一覧を取得。
    
    Returns:
        エフェクト名のリスト
    """
    return _effect_registry.list_all()


def is_effect_registered(name: str) -> bool:
    """エフェクトが登録されているかチェック。
    
    Args:
        name: エフェクト名
        
    Returns:
        登録されている場合True
    """
    return _effect_registry.is_registered(name)


def clear_registry():
    """レジストリをクリア（テスト用）。"""
    _effect_registry.clear()


def get_registry() -> BaseRegistry:
    """レジストリインスタンスを取得（ファクトリクラス用）。
    
    Returns:
        レジストリインスタンス
    """
    return _effect_registry