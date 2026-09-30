# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
memory -- the agent's MEMORY.md as code.

Design stolen from the MEMORY.md pattern: a curated long-term store,
kept tight -- durable facts, preferences, commitments, projects. Raw
day-to-day detail lives in daily logs beneath it, not in the curated
file.

Sections (each a list of dated bullets, newest understanding wins):
  facts        -- what is true about the user and the work
  preferences  -- how the user wants things done
  commitments  -- what the agent has promised or taken on
  projects     -- what is being built, and its state

Daily logs: ``append_log(dir, date, entries)`` writes
``<dir>/<date>.md`` -- the running record the curated file is
distilled from.

The template in data/memory_template.md is a clean starting memory
for any agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

TEMPLATE_NAME = "memory_template.md"
SECTIONS = ("facts", "preferences", "commitments", "projects")
_SECTION_TITLES = {
    "facts": "Facts",
    "preferences": "Preferences",
    "commitments": "Commitments",
    "projects": "Projects",
}


def _data_path() -> Path:
    return Path(__file__).resolve().parent / "data" / TEMPLATE_NAME


@dataclass
class Memory:
    """One agent's curated long-term memory."""

    facts: list[str] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)
    commitments: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)

    # -- tending -------------------------------------------------------
    def add(self, section: str, entry: str) -> None:
        """Record one durable entry. Dated bullets preferred."""
        section = section.strip().lower()
        if section not in SECTIONS:
            raise ValueError(f"unknown memory section {section!r}; "
                             f"want one of {SECTIONS}")
        entry = entry.strip()
        if entry and entry not in getattr(self, section):
            getattr(self, section).append(entry)

    def total(self) -> int:
        """How much the agent carries."""
        return sum(len(getattr(self, s)) for s in SECTIONS)

    # -- persistence ---------------------------------------------------
    @classmethod
    def from_template(cls) -> "Memory":
        """A clean starting memory, for any agent."""
        return cls.load_md(_data_path())

    @classmethod
    def load_md(cls, path: str | Path) -> "Memory":
        """Read a MEMORY.md file into a Memory."""
        text = Path(path).read_text(encoding="utf-8")
        return _parse(text)

    def save_md(self, path: str | Path) -> None:
        """Write the Memory back to a MEMORY.md file."""
        Path(path).write_text(_render(self), encoding="utf-8")

    def render(self) -> str:
        """The memory as markdown."""
        return _render(self)


def append_log(memory_dir: str | Path, date: str, entries: list[str]) -> Path:
    """Append entries to the daily log ``<memory_dir>/<date>.md``.

    ``date`` is ``YYYY-MM-DD``. Returns the log path.
    """
    log = Path(memory_dir) / f"{date}.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    existing = log.read_text(encoding="utf-8") if log.exists() else ""
    lines = [existing.rstrip()] if existing.strip() else [f"# {date}", ""]
    for e in entries:
        e = e.strip()
        if e:
            lines.append(f"- {e}")
    log.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return log


def _parse(text: str) -> Memory:
    """Parse the MEMORY.md shape: ## Sections of dated bullets."""
    mem = Memory()
    section = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            title = s[3:].strip().lower()
            section = next((k for k, v in _SECTION_TITLES.items()
                            if v.lower() == title), None)
            continue
        if section and (s.startswith("- ") or s.startswith("* ")):
            entry = s[2:].strip()
            if entry == "(none yet)":
                continue  # template filler, not an entry
            getattr(mem, section).append(entry)
    return mem


def _render(mem: Memory) -> str:
    parts = ["# MEMORY.md", "",
             "<!-- Curated long-term memory: durable facts, preferences, "
             "commitments, projects. Keep it tight; raw day-to-day detail "
             "lives in the daily logs. -->", ""]
    for key in SECTIONS:
        parts += [f"## {_SECTION_TITLES[key]}", ""]
        entries = getattr(mem, key)
        parts += [f"- {e}" for e in entries] if entries else ["- (none yet)"]
        parts += [""]
    return "\n".join(parts).rstrip() + "\n"
