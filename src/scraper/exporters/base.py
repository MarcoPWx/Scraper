#!/usr/bin/env python3
"""
Exporter interfaces and base utilities
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseExporter(ABC):
    """Base exporter interface."""

    @abstractmethod
    def export(self, **kwargs) -> Any:
        """Perform export with keyword args (format-specific)."""
        raise NotImplementedError

