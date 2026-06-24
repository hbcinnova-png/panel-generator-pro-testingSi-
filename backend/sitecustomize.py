"""HBC3 runtime compatibility shims.

Fixes old/broken paypalrestsdk wheels that import paypalrestsdk.version
even when that module is missing. Python imports sitecustomize before the
app starts, so this keeps uvicorn api:app from crashing during import.
"""
import sys
import types

if "paypalrestsdk.version" not in sys.modules:
    module = types.ModuleType("paypalrestsdk.version")
    module.__version__ = "1.13.3"
    sys.modules["paypalrestsdk.version"] = module
