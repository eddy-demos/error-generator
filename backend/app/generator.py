"""Seed-based fake error generation."""
from __future__ import annotations

import base64
import os
import random
import re
from collections import defaultdict
from typing import Optional

from sqlalchemy.orm import Session

from .models import Template, Vocab, Severity

SLOT_RE = re.compile(r"\{(\w+)\}")
BASE32_ALPHABET = "abcdefghijklmnopqrstuvwxyz234567"

SEVERITY_WEIGHTS = [
    (Severity.ERROR, 40),
    (Severity.WARNING, 25),
    (Severity.CRITICAL, 15),
    (Severity.INFO, 15),
    (Severity.EXISTENTIAL, 5),
]


def new_seed() -> str:
    raw = os.urandom(5)
    s = base64.b32encode(raw).decode("ascii").rstrip("=").lower()
    return s[:8]


def _rng_from_seed(seed: str) -> random.Random:
    return random.Random(seed)


def _gen_code(rng: random.Random) -> str:
    n_hex = rng.randint(2, 6)
    digits = "".join(rng.choice("0123456789ABCDEF") for _ in range(n_hex))
    n_alpha = rng.randint(0, 2)
    alpha = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(n_alpha))
    return f"0x{digits}{alpha}"


def _pick_severity(rng: random.Random, override: Optional[Severity]) -> Severity:
    if override is not None:
        return override
    total = sum(w for _, w in SEVERITY_WEIGHTS)
    r = rng.uniform(0, total)
    acc = 0
    for sev, w in SEVERITY_WEIGHTS:
        acc += w
        if r <= acc:
            return sev
    return Severity.ERROR


def _weighted_pick(rng: random.Random, items: list, weight_fn):
    if not items:
        return None
    weights = [max(1, weight_fn(i)) for i in items]
    total = sum(weights)
    r = rng.uniform(0, total)
    acc = 0
    for it, w in zip(items, weights):
        acc += w
        if r <= acc:
            return it
    return items[-1]


def _load_vocab(db: Session) -> dict[str, list[str]]:
    vocab = defaultdict(list)
    for row in db.query(Vocab).all():
        vocab[row.slot].append(row.value)
    return vocab


def _fill(pattern: str, rng: random.Random, vocab: dict[str, list[str]], picked: dict[str, str]) -> str:
    def sub(m: re.Match) -> str:
        slot = m.group(1)
        if slot in picked:
            return picked[slot]
        choices = vocab.get(slot, [])
        if not choices:
            return f"{{{slot}}}"
        val = rng.choice(choices)
        picked[slot] = val
        return val

    return SLOT_RE.sub(sub, pattern)


def _capitalize_first(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def generate(
    db: Session,
    severity: Optional[Severity] = None,
    subsystem: Optional[str] = None,
    seed: Optional[str] = None,
) -> dict:
    seed = seed or new_seed()
    rng = _rng_from_seed(seed)

    chosen_severity = _pick_severity(rng, severity)
    vocab = _load_vocab(db)

    # Filter title templates by kind and (optionally) severity_hint compatibility
    title_templates = (
        db.query(Template).filter(Template.kind == "title").all()
    )
    desc_templates = db.query(Template).filter(Template.kind == "description").all()

    # EXISTENTIAL uses its own pool when available
    if chosen_severity == Severity.EXISTENTIAL:
        existential_titles = [t for t in title_templates if t.severity_hint == Severity.EXISTENTIAL]
        existential_descs = [t for t in desc_templates if t.severity_hint == Severity.EXISTENTIAL]
        if existential_titles:
            title_templates = existential_titles
        if existential_descs:
            desc_templates = existential_descs
    else:
        # Exclude EXISTENTIAL-only ones from regular pool
        title_templates = [t for t in title_templates if t.severity_hint != Severity.EXISTENTIAL] or title_templates
        desc_templates = [t for t in desc_templates if t.severity_hint != Severity.EXISTENTIAL] or desc_templates

    title_tmpl = _weighted_pick(rng, title_templates, lambda t: t.weight)
    desc_tmpl = _weighted_pick(rng, desc_templates, lambda t: t.weight)

    picked: dict[str, str] = {}
    if subsystem:
        picked["subsystem"] = subsystem

    title_pattern = title_tmpl.pattern if title_tmpl else "{verb_past} {noun} into the {place}"
    desc_pattern = (
        desc_tmpl.pattern
        if desc_tmpl
        else "The {subsystem} attempted to {verb} but found only {noun}."
    )

    title = _capitalize_first(_fill(title_pattern, rng, vocab, picked))
    description = _fill(desc_pattern, rng, vocab, picked)

    final_subsystem = picked.get("subsystem") or subsystem
    if not final_subsystem:
        subsys_choices = vocab.get("subsystem", ["kernel.mood"])
        final_subsystem = rng.choice(subsys_choices)

    code = _gen_code(rng)
    tag_pool = vocab.get("tag", [])
    tags: list[str] = []
    if tag_pool:
        k = rng.randint(0, min(3, len(tag_pool)))
        tags = rng.sample(tag_pool, k) if k else []

    return {
        "code": code,
        "title": title[:120],
        "description": description[:500],
        "severity": chosen_severity,
        "subsystem": final_subsystem[:60],
        "tags": tags,
        "seed": seed,
    }
