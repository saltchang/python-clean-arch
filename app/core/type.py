from typing import Any, NewType

IDType = NewType('IDType', int)
"""
IDType is a type that represents an integer ID.
"""


JsonObject = dict[str, Any]
"""
JsonObject is a type that represents a dictionary of strings to any type.
"""
