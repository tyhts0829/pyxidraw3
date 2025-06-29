from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseEffect(ABC):
    """すべてのエフェクトのベースクラスです。ピュアな変換処理のみを担当します。"""
    
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