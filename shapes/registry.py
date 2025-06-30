"""
シェイプレジストリ - 統一されたレジストリシステム
effects/と対称性を保った@shapeデコレータの実装
"""

from typing import Dict, Type, Callable, Any
from .base import BaseShape
from common.base_registry import BaseRegistry


# 統一されたレジストリシステム
_shape_registry = BaseRegistry()


def shape(name: str):
    """シェイプをレジストリに登録するデコレータ。
    
    統一されたレジストリシステムを使用した@shapeデコレータ。
    effects/の@effectと対称性を保った実装。
    
    Usage:
        @shape("sphere")
        class Sphere(BaseShape):
            ...
    
    Args:
        name: シェイプ名
        
    Returns:
        デコレータ関数
    """
    return _shape_registry.register(name)


def get_shape(name: str) -> Type[BaseShape]:
    """登録されたシェイプクラスを取得。
    
    Args:
        name: シェイプ名
        
    Returns:
        シェイプクラス
        
    Raises:
        KeyError: シェイプが登録されていない場合
    """
    return _shape_registry.get(name)


def list_shapes() -> list[str]:
    """登録されているシェイプの一覧を取得。
    
    Returns:
        シェイプ名のリスト
    """
    return _shape_registry.list_all()


def is_shape_registered(name: str) -> bool:
    """シェイプが登録されているかチェック。
    
    Args:
        name: シェイプ名
        
    Returns:
        登録されている場合True
    """
    return _shape_registry.is_registered(name)


def clear_registry():
    """レジストリをクリア（テスト用）。"""
    _shape_registry.clear()


def get_registry() -> BaseRegistry:
    """レジストリインスタンスを取得（ファクトリクラス用）。
    
    Returns:
        レジストリインスタンス
    """
    return _shape_registry