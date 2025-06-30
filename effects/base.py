from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from common.cacheable_base import LRUCacheable


class BaseEffect(LRUCacheable, ABC):
    """すべてのエフェクトのベースクラス。キャッシング機能付きの変換処理を担当します。"""
    
    def __init__(self, maxsize: int = 128):
        super().__init__(maxsize=maxsize)
    
    @abstractmethod
    def apply(self, coords: np.ndarray, offsets: np.ndarray, **params: Any) -> tuple[np.ndarray, np.ndarray]:
        """座標とオフセット配列にエフェクトを適用します。
        
        Args:
            coords: 入力座標配列
            offsets: 入力オフセット配列
            **params: エフェクト固有のパラメータ
            
        Returns:
            (new_coords, new_offsets): 変換された座標配列とオフセット配列
        """
        pass
    
    def _execute(self, coords: np.ndarray, offsets: np.ndarray, **params: Any) -> tuple[np.ndarray, np.ndarray]:
        """実際の処理を実行（キャッシング用）"""
        return self.apply(coords, offsets, **params)
    
    def __call__(self, coords: np.ndarray, offsets: np.ndarray, **params: Any) -> tuple[np.ndarray, np.ndarray]:
        """キャッシング機能付きでエフェクトを適用"""
        return super().__call__(coords, offsets, **params)