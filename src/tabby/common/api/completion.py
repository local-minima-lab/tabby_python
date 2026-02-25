from typing import List, Optional
from pydantic import BaseModel, Field

class EditHistory(BaseModel):
    """Contains information about edit history for next edit suggestion mode."""
    original_code: str
    edits_diff: str
    current_version: str

class Declaration(BaseModel):
    """Relevant declaration code snippets provided by the editor's LSP."""
    filepath: str
    body: str

class Snippet(BaseModel):
    """A snippet of code that is relevant to the current completion request."""
    filepath: str
    body: str
    score: float

class Segments(BaseModel):
    """Main context container for the code around the cursor."""
    prefix: str
    suffix: Optional[str] = None
    filepath: Optional[str] = None
    git_url: Optional[str] = None
    declarations: Optional[List[Declaration]] = None
    relevant_snippets_from_changed_files: Optional[List[Snippet]] = None
    relevant_snippets_from_recently_opened_files: Optional[List[Snippet]] = None
    clipboard: Optional[str] = None
    edit_history: Optional[EditHistory] = None

class DebugOptions(BaseModel):
    """Options for debugging and testing completion quality."""
    raw_prompt: Optional[str] = None
    return_snippets: bool = False
    return_prompt: bool = False
    disable_retrieval_augmented_code_completion: bool = False

class CompletionRequest(BaseModel):
    """Incoming request from the IDE extension."""
    language: Optional[str] = None
    segments: Optional[Segments] = None
    user: Optional[str] = None
    debug_options: Optional[DebugOptions] = None
    temperature: Optional[float] = None
    sampling_temperature: Optional[float] = None 
    seed: Optional[int] = None
    mode: str = "standard"
    stream: bool = False
    
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = 0.0
    max_decoding_tokens: Optional[int] = 128

class Choice(BaseModel):
    """A single completion suggestion."""
    index: int = 0
    text: str

class DebugData(BaseModel):
    """Metadata returned for debugging purposes."""
    snippets: Optional[List[Snippet]] = None
    prompt: Optional[str] = None

class CompletionResponse(BaseModel):
    """Final response returned to the IDE."""
    id: str
    choices: List[Choice]
    debug_data: Optional[DebugData] = None
    mode: str = "standard"