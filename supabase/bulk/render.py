"""Markdown renderer for bulk article data. Avoid % and backslashes in content."""


def article_md(a):
    parts = [a["intro"], ""]
    for h, bullets in a["sections"]:
        parts.append("## " + h)
        parts.append("")
        for b in bullets:
            parts.append("- " + b)
        parts.append("")
    if a.get("try"):
        parts.append("## Try this week")
        parts.append("")
        for t in a["try"]:
            parts.append("- [ ] " + t)
        parts.append("")
    parts.append("> " + a["close"])
    return "\n".join(parts)


def download_md(d):
    parts = ["## How to use", ""]
    for s in d["steps"]:
        parts.append("- " + s)
    parts.append("")
    parts.append("## Tip")
    parts.append("")
    parts.append(d["tip"])
    return "\n".join(parts)
