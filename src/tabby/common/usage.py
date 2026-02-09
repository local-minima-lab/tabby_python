"""
Usage tracking and telemetry for Tabby.

Collects anonymous usage statistics to inform development priorities.
Can be disabled by setting TABBY_DISABLE_USAGE_COLLECTION environment variable.
"""

import os
import uuid
from pathlib import Path
from typing import Any, Optional
import asyncio

try:
    import httpx
except ImportError:
    # Fallback if httpx not available
    httpx = None

from . import path as path_module
from . import terminal


USAGE_API_ENDPOINT = "https://app.tabbyml.com/api/usage"


class UsageTracker:
    """Tracks and reports usage statistics."""
    
    def __init__(self):
        """Initialize the usage tracker."""
        usage_file = path_module.usage_id_file()
        
        # Create usage ID file if it doesn't exist
        if not usage_file.exists():
            # Generate new UUID
            new_id = str(uuid.uuid4())
            
            # Create parent directory if needed
            usage_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the ID
            usage_file.write_text(new_id)
            
            # Print welcome messages
            terminal.InfoMessage.print_messages([
                terminal.InfoMessage(
                    "TELEMETRY",
                    terminal.HeaderFormat.BOLD_BLUE,
                    [
                        "As an open source project, we collect usage statistics to inform development priorities. For more",
                        "information, read https://tabby.tabbyml.com/docs/configuration#usage-collection",
                        "",
                        "We will not see or collect any code in your development process."
                    ]
                ),
                terminal.InfoMessage(
                    "Welcome to Tabby!",
                    terminal.HeaderFormat.BOLD_WHITE,
                    [
                        "If you have any questions or would like to engage with the Tabby team, please join us on Slack",
                        "(https://links.tabbyml.com/join-slack-terminal)."
                    ]
                )
            ])
        
        # Read the usage ID
        self.id = usage_file.read_text().strip()
        
        # Create HTTP client if httpx is available
        if httpx:
            self.client = httpx.AsyncClient(timeout=5.0)
        else:
            self.client = None
    
    async def capture(self, event: str, properties: Any):
        """
        Capture a usage event.
        
        Args:
            event: The event name
            properties: Event properties (must be JSON serializable)
        """
        if not self.client:
            return
        
        payload = {
            "distinctId": self.id,
            "event": event,
            "properties": properties
        }
        
        try:
            await self.client.post(USAGE_API_ENDPOINT, json=payload)
        except Exception:
            # Silently fail - don't let telemetry errors break the app
            pass
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()


# Global tracker instance (lazy-initialized)
_tracker: Optional[UsageTracker] = None
_tracker_initialized = False


def _get_tracker() -> Optional[UsageTracker]:
    """Get or create the global tracker instance."""
    global _tracker, _tracker_initialized
    
    if not _tracker_initialized:
        # Check if usage collection is disabled
        if os.environ.get("TABBY_DISABLE_USAGE_COLLECTION"):
            _tracker = None
        else:
            _tracker = UsageTracker()
        _tracker_initialized = True
    
    return _tracker


async def capture(event: str, properties: Any):
    """
    Capture a usage event (async).
    
    Args:
        event: The event name
        properties: Event properties (must be JSON serializable)
    
    Example:
        await capture("server_started", {"version": "0.30.0"})
    """
    tracker = _get_tracker()
    if tracker:
        await tracker.capture(event, properties)


def capture_sync(event: str, properties: Any):
    """
    Capture a usage event (synchronous).
    
    This is a convenience wrapper that runs the async capture in a new event loop.
    Use the async version if you're already in an async context.
    
    Args:
        event: The event name
        properties: Event properties (must be JSON serializable)
    
    Example:
        capture_sync("server_started", {"version": "0.30.0"})
    """
    tracker = _get_tracker()
    if tracker:
        try:
            # Try to use existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                asyncio.create_task(tracker.capture(event, properties))
            else:
                # If no loop is running, run it
                loop.run_until_complete(tracker.capture(event, properties))
        except RuntimeError:
            # No event loop, create a new one
            asyncio.run(tracker.capture(event, properties))


async def cleanup():
    """Clean up the tracker (close HTTP client)."""
    tracker = _get_tracker()
    if tracker:
        await tracker.close()