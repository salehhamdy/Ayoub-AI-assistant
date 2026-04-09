"""
ayoub/tools/system_tools.py — System information tools.

Ported from friday-tony-stark-demo/friday/tools/system.py
Cross-platform: standard library only.
"""
import datetime
import platform


def get_current_time() -> str:
    """Return the current local datetime in ISO 8601 format."""
    return datetime.datetime.now().isoformat()


def get_system_info() -> dict:
    """Return basic system information as a dict."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }
