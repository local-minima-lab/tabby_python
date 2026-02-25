from typing import List, Optional, Tuple

def reverse_str(s: str) -> str:
    return s[::-1]

class StopCondition:
    def __init__(self, stop_words: List[str], prompt: str):
        # Reverse stop words for suffix matching (common_prefix_search on reversed text)
        self.stop_words = [reverse_str(word) for word in stop_words]
        self.reversed_text = reverse_str(prompt)
        self.num_decoded = 0

    def should_stop(self, new_text: str) -> Tuple[bool, int]:
        self.num_decoded += 1
        if not new_text:
            return False, 0

        # Update cumulative reversed text
        self.reversed_text = reverse_str(new_text) + self.reversed_text

        # In Rust, this uses a Trie. In Python, we check our reversed list.
        matched_length = 0
        for reversed_stop_word in self.stop_words:
            if self.reversed_text.startswith(reversed_stop_word):
                matched_length = max(matched_length, len(reversed_stop_word))
        
        if matched_length > 0:
            return True, matched_length
            
        return False, 0