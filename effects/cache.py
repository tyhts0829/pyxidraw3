"""
エフェクト層でのキャッシュ機構。
Geometryクラスから移動したキャッシュ機能を提供。
"""

import hashlib
from functools import wraps
from typing import Any, Callable, Dict, Tuple
import numpy as np

from engine.core.geometry import Geometry


class EffectCache:
    """エフェクト処理結果のキャッシュを管理するクラス。"""
    
    def __init__(self, max_size: int = 256):
        self.max_size = max_size
        self._cache: Dict[str, Geometry] = {}
        self._access_order = []  # LRU管理用
    
    def get(self, key: str) -> Geometry | None:
        """キャッシュから結果を取得。"""
        if key in self._cache:
            # LRU: アクセス順序を更新
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def put(self, key: str, value: Geometry) -> None:
        """キャッシュに結果を保存。"""
        if key in self._cache:
            # 既存エントリの更新
            self._access_order.remove(key)
            self._access_order.append(key)
            self._cache[key] = value
            return
        
        # 新しいエントリの追加
        if len(self._cache) >= self.max_size:
            # 最も古いエントリを削除
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[key] = value
        self._access_order.append(key)
    
    def clear(self) -> None:
        """キャッシュをクリア。"""
        self._cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得。"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "keys": list(self._cache.keys())[:5],  # 最初の5つのキーを表示
        }


# グローバルキャッシュインスタンス
_global_cache = EffectCache()


def _geometry_hash(geometry: Geometry) -> str:
    """Geometryオブジェクトのハッシュを計算。"""
    coords_bytes = geometry.coords.tobytes()
    offsets_bytes = geometry.offsets.tobytes()
    combined = coords_bytes + offsets_bytes
    return hashlib.md5(combined).hexdigest()


def _make_params_hashable(args: Tuple, kwargs: Dict[str, Any]) -> Tuple:
    """パラメータをハッシュ可能な形に変換。"""
    hashable_items = []

    # argsを処理
    for arg in args:
        if isinstance(arg, (tuple, list)):
            hashable_items.append(tuple(arg))
        elif isinstance(arg, np.ndarray):
            hashable_items.append(tuple(arg.flatten().tolist()))
        else:
            hashable_items.append(arg)

    # kwargsを処理（ソート済み）
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (tuple, list)):
            hashable_items.append((key, tuple(value)))
        elif isinstance(value, np.ndarray):
            hashable_items.append((key, tuple(value.flatten().tolist())))
        else:
            hashable_items.append((key, value))

    return tuple(hashable_items)


def _create_cache_key(operation: str, geometry: Geometry, args: Tuple, kwargs: Dict[str, Any]) -> str:
    """操作履歴を含むキャッシュキーを生成。"""
    base_hash = _geometry_hash(geometry)
    hashable_params = _make_params_hashable(args, kwargs)
    operation_str = f"{operation}:{hashable_params}"
    combined = f"{base_hash}:{operation_str}"
    return hashlib.md5(combined.encode()).hexdigest()


def cached_effect(operation_name: str):
    """エフェクト関数をキャッシュ付きにするデコレータ。
    
    Args:
        operation_name: 操作名（キャッシュキー生成に使用）
        
    Returns:
        デコレートされた関数
    """
    def decorator(func: Callable[..., Geometry]) -> Callable[..., Geometry]:
        @wraps(func)
        def wrapper(geometry: Geometry, *args, **kwargs) -> Geometry:
            # キャッシュキーを生成
            cache_key = _create_cache_key(operation_name, geometry, args, kwargs)
            
            # キャッシュを確認
            cached_result = _global_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # キャッシュミス：実際に計算
            result = func(geometry, *args, **kwargs)
            
            # 結果をキャッシュに保存
            _global_cache.put(cache_key, result)
            
            return result
        return wrapper
    return decorator


def clear_effect_cache() -> None:
    """エフェクトキャッシュをクリア。"""
    _global_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """キャッシュ統計を取得。"""
    return _global_cache.get_stats()