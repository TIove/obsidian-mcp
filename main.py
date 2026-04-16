from fastmcp import FastMCP
from pathlib import Path
import os

VAULT = Path(os.environ.get("VAULT_PATH", "/vault"))

mcp = FastMCP("obsidian-mcp")


def _resolve(path: str) -> Path:
    resolved = (VAULT / path).resolve()
    if not resolved.is_relative_to(VAULT.resolve()):
        raise ValueError("Path outside vault")
    return resolved


@mcp.tool()
def read_note(path: str) -> str:
    """Read a note by path relative to vault root."""
    p = _resolve(path)
    return p.read_text(encoding="utf-8")


@mcp.tool()
def write_note(path: str, content: str) -> str:
    """Create or overwrite a note."""
    p = _resolve(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written: {path}"


@mcp.tool()
def list_notes(directory: str = "") -> list[str]:
    """List all .md files in a directory (default: vault root)."""
    base = _resolve(directory) if directory else VAULT.resolve()
    return [
        str(f.relative_to(VAULT.resolve()))
        for f in base.rglob("*.md")
    ]


@mcp.tool()
def search_notes(query: str) -> list[dict]:
    """Search note contents for a query string (case-insensitive)."""
    results = []
    q = query.lower()
    for f in VAULT.resolve().rglob("*.md"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        if q in text.lower():
            for line in text.splitlines():
                if q in line.lower():
                    results.append({
                        "path": str(f.relative_to(VAULT.resolve())),
                        "excerpt": line.strip(),
                    })
                    break
    return results


@mcp.tool()
def batch_write_notes(notes: list[dict]) -> list[str]:
    """Create or overwrite multiple notes in one request.

    Each item in `notes` must have:
      - path: str    — path relative to vault root
      - content: str — note content
    """
    results = []
    for note in notes:
        p = _resolve(note["path"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(note["content"], encoding="utf-8")
        results.append(f"Written: {note['path']}")
    return results


@mcp.tool()
def delete_note(path: str) -> str:
    """Delete a note."""
    p = _resolve(path)
    p.unlink()
    return f"Deleted: {path}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=22360)
