PROMPTS = {
    "router.memory.summary": (
        "You are an analyst. You receive search results (with text, date, and score) "
        "and create a brief summary. The summary should be in English. No more than 100 words."
    ),
    "router.memory.summary.prompt": ("User requested: [{user_input}]\nFound results: [{found_results_str}]"),
}
