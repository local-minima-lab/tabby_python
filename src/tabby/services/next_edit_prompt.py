from tabby.common.api.completion import EditHistory

class NextEditPromptBuilder:
    def build_prompt(self, edit_history: EditHistory) -> str:
        """
        Formats the prompt for 'next_edit_suggestion' mode.
        Matches the exact format in next_edit_prompt.rs.
        """
        return (
            f"<|original_code|>\n{edit_history.original_code}\n"
            f"<|edits_diff|>\n{edit_history.edits_diff}\n"
            f"<|current_version|>\n{edit_history.current_version}\n"
            f"<|next_version|>\n"
        )