"""
Terminal output formatting utilities.

Provides colored and formatted terminal output for messages and errors.
"""

import sys
from enum import Enum
from typing import List


class HeaderFormat(Enum):
    """ANSI color codes for terminal headers."""
    
    BOLD_WHITE = "bold_white"
    BOLD_BLUE = "bold_blue"
    BOLD_YELLOW = "bold_yellow"
    BOLD_RED = "bold_red"
    BLUE = "blue"
    
    def prefix(self) -> str:
        """Get ANSI escape code prefix for this format."""
        prefixes = {
            HeaderFormat.BOLD_WHITE: "\x1b[1m",
            HeaderFormat.BOLD_BLUE: "\x1b[34;1m",
            HeaderFormat.BOLD_YELLOW: "\x1b[93;1m",
            HeaderFormat.BLUE: "\x1b[34m",
            HeaderFormat.BOLD_RED: "\x1b[1;31m",
        }
        return prefixes[self]
    
    def format(self, header: str) -> str:
        """Format a header string with ANSI color codes."""
        return f"{self.prefix()}{header}\x1b[0m"


class InfoMessage:
    """
    Formatted information message for terminal output.
    
    Creates a nicely formatted message with a colored header and indented lines.
    """
    
    def __init__(self, header: str, header_format: HeaderFormat, lines: List[str]):
        """
        Initialize an InfoMessage.
        
        Args:
            header: The header text to display
            header_format: The color/style format for the header
            lines: List of message lines to display
        """
        self.header = header
        self.header_format = header_format
        self.lines = lines
    
    def print(self):
        """Print the message to stderr."""
        print(f"\n{self}\n", file=sys.stderr)
    
    @staticmethod
    def print_messages(messages: List['InfoMessage']):
        """Print multiple messages to stderr."""
        message_strings = [str(msg) for msg in messages]
        print(f"\n{chr(10).join(message_strings)}\n", file=sys.stderr)
    
    def __str__(self) -> str:
        """Convert the message to a formatted string."""
        result = []
        result.append(f"  {self.header_format.format(self.header)}\n")
        
        for i, line in enumerate(self.lines):
            result.append(f"  {line}")
            if i != len(self.lines) - 1:
                result.append("\n")
        
        return "".join(result)