"""
Windows+Streamlit+Python3.14 fix for Playwright subprocess issue.

The problem: asyncio.subprocess in Python 3.14 has bug with ProactorEventLoop.
Playwright uses asyncio internally and fails.

Solution: Use SelectorEventLoop (Unix-style, works on Windows with Python 3.14)
"""
import threading
import queue
import asyncio
import sys
from typing import Callable, Any, TypeVar

T = TypeVar('T')


def run_playwright_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a Playwright function in a separate thread with compatible event loop.
    
    Fixes Windows+Python3.14 asyncio.subprocess NotImplementedError.
    
    Args:
        func: Function to run (should be a Playwright operation)
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        Result from func
        
    Raises:
        Exception from func if it fails
    """
    result_queue: queue.Queue[Any] = queue.Queue()
    exception_queue: queue.Queue[Exception] = queue.Queue()
    
    def worker():
        try:
            # Set event loop policy to SelectorEventLoop (compatible with Python 3.14)
            if sys.platform == 'win32':
                # On Windows with Python 3.14, ProactorEventLoop has bug
                # SelectorEventLoopPolicy works better
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            result = func(*args, **kwargs)
            result_queue.put(result)
        except Exception as e:
            import traceback
            exception_queue.put((e, traceback.format_exc()))
    
    thread = threading.Thread(target=worker, daemon=False)
    thread.start()
    thread.join()  # Wait for thread to complete
    
    # Check for exceptions
    if not exception_queue.empty():
        exc, trace = exception_queue.get()
        print(f"Error in Playwright thread: {exc}")
        print(trace)
        raise exc
    
    return result_queue.get()
