from typing import Dict


MODE_KEYWORDS: Dict[str, set[str]] = {
    "concise": {
        "brief",
        "short",
        "quick",
        "summary",
        "tldr",
        "one line",
    },
    "detailed": {
        "explain",
        "deep",
        "detail",
        "step by step",
        "comprehensive",
        "thorough",
        "compare",
    },
    "creative": {
        "story",
        "poem",
        "creative",
        "idea",
        "brainstorm",
        "imagine",
        "fiction",
    },
    "technical": {
        "code",
        "python",
        "bug",
        "error",
        "api",
        "architecture",
        "algorithm",
        "database",
        "optimize",
    },
}


def choose_mode(user_input: str, fallback: str = "detailed") -> str:
    text = user_input.lower().strip()
    if not text:
        return fallback

    scores = {mode: 0 for mode in MODE_KEYWORDS}
    for mode, keywords in MODE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[mode] += 1

    best_mode = max(scores, key=scores.get)
    return best_mode if scores[best_mode] > 0 else fallback
