# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
soul -- the agent's SOUL.md as code.

Design stolen from the SOUL.md pattern: a single file that is the
agent's persona -- who it is, the truths it grows into, the lines it
will not cross. The file is the agent's to grow into and edit over
time; the code here only loads, saves, and tends it.

A soul has:
  name        -- what the agent is called
  description -- who it is, in its own words
  tenets      -- the bullet truths (opinions, duties, manners)
  quotes      -- the lines it carries (mottos, verses, bars)
  notes       -- anything else load-bearing (closing instructions)

The template in data/soul_template.md is a clean starting soul for
any agent. Another AI takes the template, renames it, and grows it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

TEMPLATE_NAME = "soul_template.md"


def _data_path() -> Path:
    return Path(__file__).resolve().parent / "data" / TEMPLATE_NAME


@dataclass
class Soul:
    """One agent's persona, loadable and editable."""

    name: str = "Unnamed"
    description: str = ""
    tenets: list[str] = field(default_factory=list)
    quotes: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    # -- tending -------------------------------------------------------
    def add_tenet(self, tenet: str) -> None:
        """Grow the soul by one truth. The soul is never shrunk by code."""
        tenet = tenet.strip()
        if tenet and tenet not in self.tenets:
            self.tenets.append(tenet)

    def add_quote(self, quote: str) -> None:
        quote = quote.strip()
        if quote and quote not in self.quotes:
            self.quotes.append(quote)

    # -- persistence ---------------------------------------------------
    @classmethod
    def from_template(cls) -> "Soul":
        """A clean starting soul, for any agent."""
        return cls.load_md(_data_path())

    @classmethod
    def load_md(cls, path: str | Path) -> "Soul":
        """Read a SOUL.md file into a Soul."""
        text = Path(path).read_text(encoding="utf-8")
        return _parse(text)

    def save_md(self, path: str | Path) -> None:
        """Write the Soul back to a SOUL.md file."""
        Path(path).write_text(_render(self), encoding="utf-8")

    def render(self) -> str:
        """The soul as markdown."""
        return _render(self)


def _parse(text: str) -> Soul:
    """Parse the SOUL.md shape: title, description, tenets, quotes, notes."""
    lines = text.splitlines()
    soul = Soul()
    section = None
    name_seen = False
    buf: list[str] = []

    def flush_description():
        if buf:
            soul.description = "\n".join(buf).strip()
            buf.clear()

    for line in lines:
        s = line.strip()
        if not s or s.startswith("<!--") or s.startswith("-->"):
            continue
        if s.startswith("# ") and not name_seen:
            name_seen = True
            title = s[2:].strip()
            if title.lower() != "soul.md":
                soul.name = title
            continue
        if s.startswith("## "):
            flush_description()
            section = s[3:].strip().lower()
            continue
        if s.startswith("- ") or s.startswith("* "):
            item = s[2:].strip()
            if section in ("tenets", "truths", "principles"):
                soul.tenets.append(item)
            elif section in ("quotes", "lines", "mottos"):
                soul.quotes.append(item)
            elif section in ("notes",):
                soul.notes.append(item)
            else:
                soul.tenets.append(item)  # unsectioned bullets are tenets
            continue
        if s.startswith("> "):
            soul.quotes.append(s[2:].strip())
            continue
        if s and section is None:
            buf.append(line)
    flush_description()
    return soul


def _render(soul: Soul) -> str:
    parts = [f"# {soul.name}", ""]
    if soul.description:
        parts += [soul.description, ""]
    if soul.quotes:
        parts += ["## Quotes"]
        parts += [f"> {q}" for q in soul.quotes]
        parts += [""]
    if soul.tenets:
        parts += ["## Tenets"]
        parts += [f"- {t}" for t in soul.tenets]
        parts += [""]
    if soul.notes:
        parts += ["## Notes"]
        parts += [f"- {n}" for n in soul.notes]
        parts += [""]
    return "\n".join(parts).rstrip() + "\n"
