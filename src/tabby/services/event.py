# src/tabby/services/event.py

"""
Event logging service.

Writes events to daily JSON log files with async buffering.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import aiofiles

from tabby.common.api.event import EventLogger, LogEntry
from tabby.common.path import events_dir  # Fixed import


class EventWriter:
    """Async event writer that writes to daily JSON files."""
    
    def __init__(self, events_dir: Path):
        """
        Initialize event writer.
        
        Args:
            events_dir: Directory to store event files
        """
        self.events_dir = events_dir
        self.current_filename: Optional[str] = None
        self.writer: Optional[aiofiles.threadpool.binary.AsyncBufferedIOBase] = None
        
        # Create directory if it doesn't exist
        self.events_dir.mkdir(parents=True, exist_ok=True)
    
    async def write_line(self, content: str):
        """
        Write a line to the current day's event file.
        
        Args:
            content: JSON string to write
        """
        now = datetime.utcnow()
        filename = now.strftime("%Y-%m-%d.json")
        
        # Rotate to new file if day changed
        if self.current_filename != filename:
            if self.writer is not None:
                await self.writer.flush()
                await self.writer.close()
            
            filepath = self.events_dir / filename
            self.writer = await aiofiles.open(filepath, mode='a', encoding='utf-8')
            self.current_filename = filename
        
        # Write the line
        await self.writer.write(f"{content}\n")
    
    async def flush(self):
        """Flush buffered writes to disk."""
        if self.writer is not None:
            await self.writer.flush()


class EventService(EventLogger):
    """
    Event logger that writes to daily JSON files.
    
    Uses an async queue and background task for non-blocking writes.
    """
    
    def __init__(self, events_directory: Optional[Path] = None):
        """
        Initialize event service.
        
        Args:
            events_directory: Directory to store events (default: from config)
        """
        # Fix: Call events_dir() function, don't use it as default value
        self.events_dir = events_directory if events_directory is not None else events_dir()
        self.queue: asyncio.Queue[Optional[str]] = asyncio.Queue()
        self.writer_task: Optional[asyncio.Task] = None
        self._started = False
    
    async def start(self):
        """Start the background writer task."""
        if self._started:
            return
        
        self._started = True
        self.writer_task = asyncio.create_task(self._writer_loop())
    
    async def stop(self):
        """Stop the background writer task."""
        if not self._started:
            return
        
        # Signal shutdown
        await self.queue.put(None)
        
        # Wait for writer to finish
        if self.writer_task:
            await self.writer_task
        
        self._started = False
    
    async def _writer_loop(self):
        """Background task that writes events to files."""
        writer = EventWriter(self.events_dir)
        
        # Flush interval (every 5 seconds)
        last_flush = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Wait for events with timeout
                content = await asyncio.wait_for(self.queue.get(), timeout=5.0)
                
                if content is None:
                    # Shutdown signal
                    await writer.flush()
                    break
                
                await writer.write_line(content)
                
                # Periodic flush
                now = asyncio.get_event_loop().time()
                if now - last_flush >= 5.0:
                    await writer.flush()
                    last_flush = now
                    
            except asyncio.TimeoutError:
                # Flush on timeout
                await writer.flush()
                last_flush = asyncio.get_event_loop().time()
    
    def write(self, entry: LogEntry):
        """
        Write a log entry to the queue.
        
        Args:
            entry: LogEntry to write
        """
        try:
            # Serialize to JSON
            json_str = entry.model_dump_json()
            
            # Add to queue (non-blocking)
            try:
                asyncio.create_task(self.queue.put(json_str))
            except RuntimeError:
                # If no event loop, use sync method (for testing)
                import logging
                logging.warning("No event loop available, event not logged")
                
        except Exception as e:
            import logging
            logging.error(f"Failed to serialize event: {e}")


# Global event service instance
_event_service: Optional[EventService] = None


def create_event_logger() -> EventLogger:
    """
    Create or get the global event logger instance.
    
    Returns:
        EventLogger instance
    """
    global _event_service
    
    if _event_service is None:
        _event_service = EventService()
    
    return _event_service


async def start_event_service():
    """Start the event service background task."""
    global _event_service
    
    if _event_service is None:
        _event_service = EventService()
    
    await _event_service.start()


async def stop_event_service():
    """Stop the event service background task."""
    global _event_service
    
    if _event_service is not None:
        await _event_service.stop()