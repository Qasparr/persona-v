# ☉ in 3° 57′ Libra  ☽ in 8° 36′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
naming -- gender and sexuality of the 72 names, and the user's say.

    "And out of the ground the LORD God formed every beast of the
    field, and every fowl of the air; and brought them unto Adam to
    see what he would call them: and whatsoever Adam called every
    living creature, that was the name thereof." -- Genesis 2:19

Hypothesis
----------
An officer's gender and sexuality can be assessed from behavior --
what the office does, not what it is called -- and the assessment
can be held honestly without being made operative.

Method
------
Behavioral assessment per office and duty. Gender: male at the
martial/severing pole (severing, breaking, driving, executing,
championing, taming, lawgiving, purging under command); female at
the containant/tending pole (tending, midwifing, weaving, bearing,
keeping refuge, nursing, healing, gathering, guarding waters and
depths, composting renewal); nonbinary by default (measuring,
keeping, watching, guarding thresholds, interpreting, weighing,
heralding, mixing opposites, judging by balance -- no binary marker
found). Sexuality: abstinent by default -- and in the first pass
(2026-09-26), all 72: no office's behavior carries an erotic
character; the officers' eros is sublimated into office. A binary
assignment is made only where the assessment positively finds a
marker; in doubt, the default stands. Every assessment is recorded
per name in names.yaml under "assessment" -- the author's to
red-pen. Whether the binary assignments make a difference is decided
by the device's current user (~/.persona-v/config.yaml, naming:
binary, default false; PERSONA_V_NAMING_BINARY overrides for tests
and drivers). false: the names remain nonlinear and fluid -- the
recorded gender and sexuality are not operative, sortition draws
from the whole choir, officers render without gender. true: the
assessed gender and sexual preference are operative and surfaced --
every officer listing names them, and the Master/Apprentice
rendering reads the anima/animus polarity honestly
(pair_polarity_reading).

Observation
-----------
chair_pole(): each chair's pole from its drawn officers.
pair_polarity_reading(): one honest line -- cross-wise syzygy,
intramural same-pole, or unmarked where neither chair holds a clear
binary majority.

Result
------
Decided 2026-09-26 under the author's leave: the binary setting
makes the assignments legible, never operative. Nothing is gated --
no office closed to any gender; sortition stays uniform; polarity
never weights an election or scores a compatibility. The fluid
policy reads nothing, as before.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML ships with the package
    yaml = None

GENDERS = ("nonbinary", "male", "female")
SEXUALITIES = ("abstinent", "androphilic", "gynephilic", "ambiphilic")

#: What a name reads as when the user's policy keeps things fluid.
FLUID = "fluid"


def _default_config_path() -> Path:
    return Path.home() / ".persona-v" / "config.yaml"


def _env_override() -> bool | None:
    raw = os.environ.get("PERSONA_V_NAMING_BINARY")
    if raw is None:
        return None
    return raw.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class NamingPolicy:
    """The device's current user's decision about binary assignments."""
    binary: bool = False
    source: str = "default"  # "env" | "config" | "default"

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> "NamingPolicy":
        """Read the user's decision: env override, then config file."""
        env = _env_override()
        if env is not None:
            return cls(binary=env, source="env")
        path = Path(config_path).expanduser() if config_path is not None \
            else _default_config_path()
        if path.exists() and yaml is not None:
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except (yaml.YAMLError, OSError):
                raw = {}
            naming = raw.get("naming", {}) if isinstance(raw, dict) else {}
            if isinstance(naming, dict) and "binary" in naming:
                return cls(binary=bool(naming["binary"]), source="config")
        return cls()

    def describe(self) -> str:
        if self.binary:
            return ("naming policy: BINARY (source: "
                    f"{self.source}) -- assessed gender and sexual "
                    "preference are operative and surfaced")
        return ("naming policy: FLUID (source: "
                f"{self.source}) -- names remain nonlinear; either male "
                "or female names work for any office")


def write_binary_setting(value: bool,
                         config_path: str | Path | None = None) -> Path:
    """Write the user's binary/fluid decision to the config file.

    Creates parent directories as needed and preserves every other
    existing key in the file -- only ``naming.binary`` is set.
    Returns the path written.
    """
    path = Path(config_path).expanduser() if config_path is not None \
        else _default_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if path.exists() and yaml is not None:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data = raw
        except (yaml.YAMLError, OSError):
            data = {}
    naming = data.get("naming")
    if not isinstance(naming, dict):
        naming = {}
        data["naming"] = naming
    naming["binary"] = bool(value)
    if yaml is None:  # pragma: no cover - PyYAML ships with the package
        raise RuntimeError("PyYAML is required to write the naming config")
    path.write_text(yaml.safe_dump(data, sort_keys=False,
                                   default_flow_style=False),
                    encoding="utf-8")
    return path


def validate_gender(gender: str) -> str:
    if gender not in GENDERS:
        raise ValueError(f"gender must be one of {GENDERS}, got {gender!r}")
    return gender


def validate_sexuality(sexuality: str) -> str:
    if sexuality not in SEXUALITIES:
        raise ValueError(f"sexuality must be one of {SEXUALITIES}, "
                         f"got {sexuality!r}")
    return sexuality


def effective_gender(name, policy: NamingPolicy) -> str:
    """The gender under which this officer serves.

    Fluid policy: every officer serves as fluid -- the recorded
    assignment is not operative. Binary policy: the assessed gender.
    """
    if not policy.binary:
        return FLUID
    return validate_gender(name.gender)


def effective_sexuality(name, policy: NamingPolicy) -> str:
    """The sexuality under which this officer serves (same rule)."""
    if not policy.binary:
        return FLUID
    return validate_sexuality(name.sexuality)


def render_officer(name, policy: NamingPolicy) -> str:
    """One line: number, name, office, and gender standing."""
    return (f"{name.number}. {name.name} -- {name.office} "
            f"({effective_gender(name, policy)} / "
            f"{effective_sexuality(name, policy)})")


def chair_pole(numbers, names: dict, policy: NamingPolicy) -> str:
    """The pole a chair speaks from in this working.

    ``numbers`` are the drawn officer numbers; ``names`` maps number
    to Name. Returns ``"masculine"`` / ``"feminine"`` by majority of
    the binary-marked officers drawn, else ``"unmarked"`` -- ties,
    all-nonbinary draws, and the fluid policy all decline to declare.
    A pole is a reading of *this working's* invoked faces, not an
    attribute of the flavor.
    """
    if not policy.binary:
        return "unmarked"
    votes: dict[str, int] = {}
    for n in numbers:
        g = names[n].gender  # the assessed gender, not the fluid mask
        if g in ("male", "female"):
            votes[g] = votes.get(g, 0) + 1
    if not votes:
        return "unmarked"
    ranked = sorted(votes.items(), key=lambda kv: kv[1], reverse=True)
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return "unmarked"
    return "masculine" if ranked[0][0] == "male" else "feminine"


def pair_polarity_reading(master_numbers, apprentice_numbers,
                          names: dict, policy: NamingPolicy) -> str | None:
    """
    One honest line on the pair's anima/animus polarity.
    
    Hypothesis: the drawn officers' assessed genders can be read
    honestly without being made operative. Method: read each chair's
    pole from its officers under the binary policy (None under fluid).
    Observation: cross-wise syzygy, intramural same-pole, or unmarked
    where neither chair holds a clear binary majority. Result: legible,
    never operative -- it gates nothing, weights nothing, scores
    nothing, and never touches sortition or election. Sexuality is not
    read: all 72 assess abstinent, and there is no variance to be honest
    about.
    """
    if not policy.binary:
        return None
    m = chair_pole(master_numbers, names, policy)
    a = chair_pole(apprentice_numbers, names, policy)
    if m == "unmarked" or a == "unmarked":
        return ("Polarity: unmarked on one or both chairs -- the reading "
                "stays fluid here; the contrarian's face is not declared.")
    if m == a:
        return (f"Polarity: both chairs speak from the {m} pole -- the "
                "contrarian wears the same face; the cross-examination "
                "is intramural.")
    return (f"Polarity: the Master speaks from the {m} pole, the "
            f"Apprentice answers from the {a} pole -- the syzygy "
            "stands cross-wise, anima against animus.")


def inspect_name(name, policy: NamingPolicy) -> str:
    """Full inspection of one officer: the red-pen view."""
    lines = [
        f"{name.number}. {name.name} -- {name.office}",
        f"Duty: {name.duty}",
        f"Motto: {name.motto} ({name.gloss})",
        f"Assessed gender: {name.gender}; assessed sexuality: "
        f"{name.sexuality}",
        f"Assessment: {name.assessment or 'none recorded'}",
        f"Effective under current policy: {effective_gender(name, policy)} "
        f"/ {effective_sexuality(name, policy)}",
        policy.describe(),
    ]
    return "\n".join(lines)
