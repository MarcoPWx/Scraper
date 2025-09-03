#!/usr/bin/env python3
from __future__ import annotations

"""
Importer interfaces and base utilities
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseImporter(ABC):
    """Base importer interface."""

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the import. Returns a summary dict."""
        raise NotImplementedError
