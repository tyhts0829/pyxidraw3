"""
Shapes module - Internal shape implementations

This module provides the internal shape implementations used by the API layer.

For public API usage, use G from api.shape_factory instead of importing directly.

Example:
    # Recommended public API
    from api import G
    sphere = G.sphere(subdivisions=0.5)
    
    # Direct import (internal use only)
    from shapes.sphere import sphere_data
"""

from .base import BaseShape
from .polygon import Polygon
from .sphere import Sphere
from .grid import Grid
from .polyhedron import Polyhedron
from .lissajous import Lissajous
from .torus import Torus
from .cylinder import Cylinder
from .cone import Cone
from .capsule import Capsule
from .attractor import Attractor
from .text import Text
from .asemic_glyph import AsemicGlyph

__all__ = [
    "BaseShape",
    "Polygon",
    "Sphere", 
    "Grid",
    "Polyhedron",
    "Lissajous",
    "Torus",
    "Cylinder",
    "Cone",
    "Capsule",
    "Attractor",
    "Text",
    "AsemicGlyph",
]