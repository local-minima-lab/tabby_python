from typing import List, Optional, Tuple
from tabby.common.api.completion import Segments, Snippet

class PromptBuilder:
    def __init__(self, code_search_params, prompt_template: Optional[str], code_search=None):
        self.code_search_params = code_search_params
        self.prompt_template = prompt_template
        self.code_search = code_search

    def build(self, language: str, segments: Segments, snippets: List[Snippet]) -> str:
        # 1. Inject snippets as comments into the prefix
        prefix = self._build_prefix(language, segments.prefix, snippets)
        
        # 2. Get default suffix (newline if empty)
        suffix = segments.suffix if segments.suffix and segments.suffix.strip() else "\n"
        
        # 3. Apply FIM template (e.g., <PRE> {prefix} <SUF>{suffix} <MID>)
        if not self.prompt_template:
            return prefix
        return self.prompt_template.format(prefix=prefix, suffix=suffix)

    def _build_prefix(self, language: str, prefix: str, snippets: List[Snippet]) -> str:
        if not snippets:
            return prefix
            
        # Simplified comment logic; real version would use a language registry
        comment_char = "#" if language.lower() in ["python", "yaml"] else "//"
        
        lines = []
        for i, snippet in enumerate(snippets):
            lines.append(f"Path: {snippet.filepath}")
            lines.extend(snippet.body.splitlines())
            if i < len(snippets) - 1:
                lines.append("")

        comments = "\n".join([f"{comment_char} {l}".strip() or comment_char for l in lines])
        return f"{comments}\n{prefix}"

    def extract_snippets(self, segments: Segments, max_chars: int = 768) -> List[Snippet]:
        """
        Priority-based snippet extraction from the request:
        1. LSP Declarations
        2. Changed Files
        3. Recently Opened Files
        """
        ret = []
        curr_len = 0
        sources = [
            segments.declarations or [],
            segments.relevant_snippets_from_changed_files or [],
            segments.relevant_snippets_from_recently_opened_files or []
        ]
        
        for source in sources:
            for item in source:
                if curr_len + len(item.body) > max_chars:
                    break
                curr_len += len(item.body)
                ret.append(Snippet(filepath=item.filepath, body=item.body, score=1.0))
        return ret