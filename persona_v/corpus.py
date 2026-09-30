"""
Honest reference-library catalogue for the eight surveyed PDF documents.

Hypothesis: a reference library is only as honest as its verdicts. A list of
titles without judgements is not a library; it is a rumor.

Method: every document in the surveyed corpus carries a fixed Verdict that
separates usable reference from unverified material. Toy, placeholder, and
chatbot-output markers are named in the document's caveats, quoted briefly,
so no entry can be mistaken for something it is not. Nothing in this module
presents pasted-AI-output code as tested, deployed, or authoritative.

Observation: the corpus as surveyed — one Johnathan-authored Thoth codex,
six pasted AI-chat outputs of varying technical substance, and one
factually-grounded procedure. Several PDFs contain real, usable patterns
(AArch64 boot shape, mbedTLS recipes, C++23 scoring, a Samsung/Magisk
workflow) wrapped in chatbot packaging; several contain pure stagecraft
(toy moduli, one-bit "quantum" seeds, century-long certificates).

Result: the catalogue below. Doctrine-level data (the codex) becomes engine
data only after Johnathan's red pen; reference material becomes patterns
and recipes only; reference-only material stays idea sketch; the procedure
stays unverified-by-us. Oz x Duty applies: the right to cite a document is
multiplied by the duty to state its verdict.

Run:  python3 tests/test_corpus.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# -- verdict constants -----------------------------------------------------
# Plain strings, kept as module-level constants so engines can compare
# without conjuring new vocabulary.

#: Author-authored synthesis; usable as engine data only after the
#: author's red pen.
DOCTRINE = "doctrine"

#: Technically substantive but unverified — patterns and recipes only,
#: never presented as tested or working.
REFERENCE = "reference"

#: Idea sketch or chatbot output — do not treat as a working mechanism.
REFERENCE_ONLY = "reference-only"

#: Factually grounded how-to, still unverified by us.
PROCEDURE = "procedure"

VALID_VERDICTS = (DOCTRINE, REFERENCE, REFERENCE_ONLY, PROCEDURE)


# -- document --------------------------------------------------------------

@dataclass(frozen=True)
class Document:
    """One surveyed document, with its honesty markers attached.

    `verdict` is one of the four Verdict constants. `caveats` must never
    be empty: every document carries its toy/placeholder/unverified
    markers, quoted briefly. `author_note` names the provenance in one
    line (e.g. "Johnathan-authored" vs "pasted AI-chat output").
    """

    id: str
    title: str
    filename: str
    pages: int
    summary: str
    verdict: str
    caveats: list[str] = field(default_factory=list)
    author_note: str = ""


# -- the catalogue ----------------------------------------------------------

DOCUMENTS: tuple[Document, ...] = (
    Document(
        id="codex",
        title="Thoth Tarot: The Grand Unified Architecture & Codex",
        filename="Thoth_Tarot_Grand_Unified_Codex_11_rvet.pdf",
        pages=4,
        summary=(
            "Johnathan-authored synthesis of Thelemic/Hermetic axioms, the "
            "22 Atu as 22 paths of the Tree of Life, a full 12-sign x 3-decan "
            "minor-arcana timing table, court-card/Tetragrammaton attributions, "
            "elemental dignities with a worked triad case study, and a 5-step "
            "Opening of the Key procedure. Records his coinages verbatim: the "
            "Dictum fix \"Every Man, Woman, and Child, is a Star\", the Ma'at "
            "dictum (the PDF renders it as \"Live, Love, and let Love, Live!\" "
            "under the heading \"Dictuum\" — exclamation and typo recorded, "
            "not corrected), the Golden Rule as the Only Rule, and the "
            "Tzaddi/Heh switch citing Liber AL I:57. Machine-consumable "
            "readings-engine data: dignities rules, decan table, OOTK steps."
        ),
        verdict=DOCTRINE,
        caveats=[
            "every [cite: N] is an unresolved placeholder — no real bibliography",
            "nothing verified against the printed Book of Thoth",
            'the Ma\'at dictum renders as "Live, Love, and let Love, Live!" — '
            "exclamation mark, and the \"Dictuum\" typo, recorded not corrected",
            "jurisprudence section (Bonham's, Yick Wo, UCC 1-308) is gloss-summary, not legal authority",
            "Murphy's Law (\"What can occur — will.\" = 93) is absent from this document",
            "usable as engine data only after Johnathan's red pen",
        ],
        author_note="Johnathan-authored",
    ),
    Document(
        id="armv93",
        title="Architectural Implementation Plan Armv9.3",
        filename="Architectural_Implementation_Plan_Armv9.3__13_q8uo.pdf",
        pages=9,
        summary=(
            "Two-module bare-metal AArch64 \"trust\" payload targeting "
            "Snapdragon 695 (2x Cortex-A78 + 6x Cortex-A55): boot_core.S "
            "(EL3->EL1 drop, core parking, MMU setup) plus isolated_trust.c "
            "(identity-mapped page tables, a \"trust validation\" routine, a "
            "payload jump on success). Structurally plausible boot shape; the "
            "cryptography inside is theater."
        ),
        verdict=REFERENCE,
        caveats=[
            '"trust validation" is a DJB2 hash (seed 1331) compared byte-wise '
            "against an XOR accumulator — not RSA, not any signature scheme",
            "hardcoded toy modulus literal (0xAB, 0xCD, 0xEF, 0x01, 0x23, ... "
            "ascending-counting pattern) — obviously fabricated",
            "assembly label uses Chinese characters 死循环 (\"infinite loop\") "
            "— copy-paste artifact from a Chinese-language chatbot session",
            'author field is a placeholder: "[User Specified Name / System '
            'Operator]"',
            '"Armv9.3" in the title, zero Armv9.3 features inside — Armv8-A baseline code',
            "never presented as verified or working: unverifiable without hardware",
        ],
        author_note="pasted AI-chat output",
    ),
    Document(
        id="sgmek",
        title="The Sovereign Grand Master Enterprise Key (SGMEK) Framework",
        filename="The_Sovereign_Grand_Master_Enterprise_Key__SGMEK__Framework_12_5eb8.pdf",
        pages=6,
        summary=(
            "Concept paper fusing Armv9-A hardware security (RME, PAC, SVE2) "
            "with \"Topological Quantum Computing\": a numeric-constants table "
            "assigning 11/33/47/63/74/93/1331/1776 dual architectural and "
            "\"quantum-cryptographic\" roles, plus three prose pseudo-algorithms. "
            "Numbers 93/1331/1776 align with Johnathan's existing gnosis; "
            "nothing here is a working mechanism."
        ),
        verdict=REFERENCE_ONLY,
        caveats=[
            'leaked generation footer: "Gemini 3.1 Pro Thinking level = Extended '
            'Complexity" followed by "PROMPT WAS / Expand on how the nunbers '
            '11 33 47 63 74 93 1331 ..." (sic: "nunbers") — raw chatbot provenance',
            "numerology presented as hardware spec (e.g. 74-bit custom "
            "instruction — A64 instructions are architecturally fixed at 32 bits)",
            "no code, no math, no benchmarks, no proofs, no citations",
            "absorb as an idea sketch only — never as a working mechanism",
        ],
        author_note="pasted AI-chat output",
    ),
    Document(
        id="byzantine",
        title="Phase XXVI: Distributed Asynchronous Byzantine Fault Detection Framework",
        filename="Phase_XXVI__Distributed_Asynchronous_Byzantine_Fault_Detection_Framework__Asynchronous_Behavioral_Invariant_Validation_Engine__14_nk0x.pdf",
        pages=12,
        summary=(
            "One module of a long \"Phase\" roadmap for a hypothetical drone "
            "cluster: a ~230-line C++23 DistributedByzantineDetectorEngine "
            "(weighted anomaly score, EMA smoothing, quarantine thresholds, "
            "peer registry). Genuinely compilable-quality scoring/registry "
            "pattern for anomaly triage — the most real code artifact in the "
            "corpus. No consensus protocol despite the name."
        ),
        verdict=REFERENCE,
        caveats=[
            "hardware quarantine hook is a no-op: (void)maliciousNodeId; return true",
            "no BFT consensus despite the name — threshold scoring only, "
            "no PBFT view changes, no quorum math; never cite as a BFT implementation",
            'closes in chatbot voice: "Where should we direct the architectural '
            'deployment sequence next?..."',
            'theatrical status prints ("BYZANTINE ISOLATION SYSTEM INTERLOCK '
            'ENGAGED" banner)',
            "fantasy context: the 50-node \"Killah Beez\" drone cluster is a "
            "fictional product universe",
            "never presented as verified or working in deployment",
        ],
        author_note="pasted AI-chat output",
    ),
    Document(
        id="masterkey",
        title="SCJ Sovereign Authority Enterprise Masterkey Generator",
        filename="SCJ_SOVEREIGN_AUTHORITY_ENTERPRISE_MASTERKEY_GENER..._15_vs8o.pdf",
        pages=6,
        summary=(
            "\"Freestanding, baremetal AArch64\" design for generating a 512-bit "
            "master key via a hardened mbedTLS stack: stripped "
            "mbedtls_config.h, RNDR entropy idiom, CTR-DRBG seeding, secure "
            "wipe, GCC freestanding flags matrix. Technically sound as a "
            "bare-metal mbedTLS port checklist; never compiled or run."
        ),
        verdict=REFERENCE,
        caveats=[
            'opens in chatbot voice: "Here is the complete blueprint and '
            'implementation for a freestanding, baremetal AArch64 environment..."',
            'placeholder author: "[Your Name / SCJ Sovereign Authority]" — never filled in',
            "UART print writes are commented out, so all [STATUS]/[ERROR] output "
            "goes nowhere on real hardware",
            "sizeof(pers_string) passes the pointer size (8), not the string length",
            "master_key_buffer is static and never actually cleared",
            "never compiled, run, or tested — plausible port recipe only",
        ],
        author_note="pasted AI-chat output",
    ),
    Document(
        id="certgen",
        title="SCJ Sovereign Masterkey Certificate Generator",
        filename="SCJ_Sovereign_Masterkey_Certificate_Generator__structured_as_an_independent_baremetal_AArch64_payload._16_dae4.pdf",
        pages=8,
        summary=(
            "Baremetal AArch64 payload generating a SECP384R1 keypair and "
            "self-signing an X.509 root CA via mbedTLS: linker script, "
            "startup.S, the m_bedtls_x509write_crt_* API sequence (validity, "
            "basic constraints, key usage, PEM output), and a production "
            "compile matrix (aarch64-none-elf-gcc, objcopy -O binary). "
            "Strongest single-file crypto API recipe in the corpus; the "
            "deployment story around it is fantasy."
        ),
        verdict=REFERENCE,
        caveats=[
            "absurd certificate validity: 10-year root (2026-07-03 -> 2036-07-03), "
            "hardcoded — a red flag, never presented as sound practice",
            "prints the private key over UART by design — "
            "key-exfiltration-by-design, never presented as secure practice",
            'chatbot voice: "Here is the complete production-grade blueprint..." '
            "— \"production-grade\" is the document's word, not this module's",
            "EDL-boot deployment claim ignores secure boot, fuse state, and "
            "bootloader signing on retail hardware",
            "the 64 KB \"crypto heap\" is never wired into mbedTLS's allocator",
            "not compiled, not run, not tested — a plausible recipe, no demonstrated artifact",
        ],
        author_note="pasted AI-chat output",
    ),
    Document(
        id="authcert",
        title="Universal Sovereign Authority: Certificate of Authorship & License",
        filename="Generate_self_signed_certificate_of_authorship_lic..._18_ix1u.pdf",
        pages=6,
        summary=(
            "Five-phase \"handover\" script collection (XML manifest, Q#, Lua, "
            "Python, TCL Eggdrop, PowerShell, Bash) for generating a self-signed "
            "RSA-4096 authorship certificate and signing an Android 17 AOSP "
            "userdebug build. The OpenSSL recipe itself is real and correct; "
            "everything around it is stagecraft."
        ),
        verdict=REFERENCE_ONLY,
        caveats=[
            "100-year certificate validity (-days 36500) — the most egregious "
            "numeric placeholder in the corpus",
            'the Q# "quantum entropy" phase returns one classical bit — it '
            "cannot seed RSA-4096",
            "the avbtool signing call is commented out while the script prints "
            '"[+] Baremetal Secure Boot Compliance Achieved"',
            'Lua "hardware mapping" is print() statements — a simulation log, '
            "not a root of trust",
            'certificate CN is "HNIC Starship Enterprise" — stagecraft in the subject',
            "private key written to the working directory in cleartext, no "
            "permission hardening",
            "usable as a correct OpenSSL self-sign recipe; the rest is stagecraft",
        ],
        author_note="pasted AI-chat output",
    ),
    Document(
        id="magisk",
        title="Magisk Manager guide: rooting the Samsung Galaxy Tab A9+",
        filename="yes_to_use_magisk_managerif_possible_17_9q74.pdf",
        pages=3,
        summary=(
            "Step-by-step procedure for rooting the Galaxy Tab A9+ (SM-X210 "
            "Wi-Fi / SM-X216 5G) with the official Magisk app: exact stock "
            "firmware download (Frija/Bifrost/SamFw/SamMobile), AP-tar patching "
            "on-device, Odin3 flash (non-HOME CSC on first flash), Direct "
            "Install of the stub. The most factually grounded procedural "
            "document in the corpus; framing and citations are AI packaging."
        ),
        verdict=PROCEDURE,
        caveats=[
            'strip the chatbot upsell close: "Do you want to try loading a '
            'custom AOSP / LineageOS GSI...?"',
            "citation list [1]-[15] resolves to bare domains (youtube.com, "
            "github.com, reddit.com), not specific pages — domain-only, cannot "
            "substantiate claims",
            '"absolute su kernel-level execution rights" overstates what Magisk '
            "provides",
            "rooting trips Knox permanently and voids warranty — unstated in "
            "the document",
            "procedure is accurate as described, still unverified by us",
        ],
        author_note="pasted AI-chat output",
    ),
)

#: Id lookup order.
_IDS = tuple(d.id for d in DOCUMENTS)

_ID_MAP = {d.id: d for d in DOCUMENTS}


# -- accessors --------------------------------------------------------------

def document(doc_id: str) -> Optional[Document]:
    """Return the Document for `doc_id`, or None on unknown ids — never invents."""
    return _ID_MAP.get(doc_id)


def document_ids() -> list[str]:
    """Return the eight catalogue ids, in catalogue order."""
    return list(_IDS)


def by_verdict(v: str) -> list[Document]:
    """Return all Documents carrying verdict `v` (empty list if none)."""
    return [d for d in DOCUMENTS if d.verdict == v]


def honesty_report() -> str:
    """Plain-text one-line-per-document summary.

    Each line is "id: verdict — <first caveat>". Every document carries
    at least one caveat, so no line can silently claim purity.
    """
    lines = [
        "CORPUS HONESTY REPORT — one line per document; "
        "first caveat is the document's loudest warning:"
    ]
    for d in DOCUMENTS:
        first = d.caveats[0] if d.caveats else "no caveats"
        lines.append(f"{d.id}: {d.verdict} — {first}")
    return "\n".join(lines)
