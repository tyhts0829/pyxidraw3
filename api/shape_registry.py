"""
形状レジストリシステム - レジストリパターンによる拡張可能な形状管理。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Type, Union

from engine.core.geometry_data import GeometryData

# グローバル形状レジストリ
SHAPE_REGISTRY: Dict[str, Union[Type, Callable]] = {}


def register_shape(name: str):
    """形状クラスまたは関数をレジストリに登録するデコレータ。
    
    Args:
        name: 形状の登録名（G.sphere() のように使用される）
    
    Usage:
        @register_shape("star")
        class StarShape:
            def generate(self, **params) -> GeometryData:
                # 形状生成ロジック
                pass
    """
    def decorator(cls_or_func):
        SHAPE_REGISTRY[name] = cls_or_func
        return cls_or_func
    return decorator


def get_shape_generator(name: str):
    """登録された形状生成器を取得。"""
    if name not in SHAPE_REGISTRY:
        raise ValueError(f"Unknown shape: {name}")
    return SHAPE_REGISTRY[name]


def list_registered_shapes() -> List[str]:
    """登録されているすべての形状名を返す。"""
    return sorted(list(SHAPE_REGISTRY.keys()))


def unregister_shape(name: str):
    """形状の登録を解除（主にテスト用）。"""
    if name in SHAPE_REGISTRY:
        del SHAPE_REGISTRY[name]


class CustomShape(ABC):
    """ユーザー定義形状の基底クラス。"""
    
    @abstractmethod
    def generate(self, **params) -> GeometryData:
        """形状を生成する抽象メソッド。
        
        Args:
            **params: 形状生成パラメータ
            
        Returns:
            GeometryData: 生成された形状データ
        """
        pass


class ValidatedCustomShape(CustomShape):
    """パラメータ検証機能付きカスタム形状基底クラス。"""
    
    def get_default_params(self) -> dict:
        """デフォルトパラメータを定義。"""
        return {}
    
    def validate_params(self, **params) -> dict:
        """パラメータを検証し、デフォルト値を適用。"""
        defaults = self.get_default_params()
        validated = {**defaults, **params}
        self._validate_impl(validated)
        return validated
    
    def _validate_impl(self, params: dict):
        """パラメータ検証ロジック（サブクラスでオーバーライド可能）。"""
        pass
    
    def generate(self, **params) -> GeometryData:
        validated_params = self.validate_params(**params)
        return self._generate_impl(**validated_params)
    
    @abstractmethod
    def _generate_impl(self, **params) -> GeometryData:
        """実際の生成ロジック（サブクラスで実装）。"""
        pass