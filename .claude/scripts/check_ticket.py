#!/usr/bin/env python3
"""Check a ticket draft against the vault templates before it is shown or sent to Linear.

Usage: check_ticket.py --kind standard|epic|design --team DEV|DES --file draft.md
Exits 1 and prints one FAIL line per problem; exits 0 when the draft is clean.
The required structure is read from Templates/Tickets/ so the template stays canonical.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "Templates", "Tickets"))
DEFAULT_CONFIG = {"build_team": "DEV", "design_team": "DES", "design_tag": "[DESIGN] - "}


def load_config(path=None):
    """Team keys and the design title tag. Read from .claude/pm-config.json if it exists,
    or from the file named by the PM_CONFIG environment variable. Missing keys use the defaults."""
    cfg = dict(DEFAULT_CONFIG)
    path = path or os.environ.get("PM_CONFIG") or os.path.join(HERE, "..", "pm-config.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            cfg.update({k: v for k, v in json.load(fh).items() if k in DEFAULT_CONFIG})
    return cfg


CONFIG = load_config()
TEAMS = (CONFIG["build_team"], CONFIG["design_team"])
DESIGN_TAG = CONFIG["design_tag"]
NON_VERB_STARTS = {"the", "a", "an", "epic", "ticket", "new", "and", "for", "to", "of", "in", "on", "with"}
BANNED = [
    (r"\bTBC\b", "TBC"),
    (r"\bTBD\b", "TBD"),
    (r"\bWIP\b", "WIP"),
    (r"\bRESOLVED\b", "RESOLVED"),
    (r"\bupdated?\s*[:\-–]", "an update line"),
    (r"\bupdate\s+\d{1,2}\s+[A-Za-z]{3}", "an update line"),
]
MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
DATED = re.compile(
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+" + MONTHS + r"\b"
    r"|\b" + MONTHS + r"\s+\d{1,2}\b"
    r"|\b\d{4}-\d{2}-\d{2}\b"
    r"|\b(?:yesterday|this week|last week|this morning)\b",
    re.I,
)
SCOPE_STATEMENT = re.compile(r"^(?:not in|out of scope)\b", re.I)
SECTION6_BANNED = re.compile(r"out of scope|proposed|child and parent|reorgani|change ?log|update", re.I)
STORY = re.compile(r"^\*As an? .+, I want to .+, so that .+\.\*$")


LEGACY_DIR = os.path.join(HERE, "legacy_templates")


def read_template(kind, legacy=False):
    folder = LEGACY_DIR if legacy else TEMPLATE_DIR
    with open(os.path.join(folder, kind + ".md"), encoding="utf-8") as fh:
        return fh.read()


def is_legacy(text, kind):
    """True for a draft in the old template: a standard ticket with an old heading (Expected behaviour,
    Acceptance criteria, Potential impacts) but no Requirements heading, or an epic without the Design references section."""
    if kind == "standard":
        heads = bold_headings(text)
        old = {"Expected behaviour", "Acceptance criteria", "Potential impacts"}
        return bool(old & set(heads)) and "Requirements" not in heads
    if kind == "epic":
        return not re.search(r"^## (?:6\.\s*Design references|7\.\s*What we know|8\.\s*Readiness summary)", text, re.M)
    return False


def bold_headings(text):
    return [m.group(1).strip() for m in re.finditer(r"^\*\*(.+?)\*\*\s*$", text, re.M)]


def section_bodies(text):
    """Map each bold heading to the lines beneath it."""
    out, name = {}, None
    for line in text.splitlines():
        m = re.match(r"^\*\*(.+?)\*\*\s*$", line)
        if m:
            name = m.group(1).strip()
            out[name] = []
        elif name is not None:
            out[name].append(line)
    return out


def template_labels(body_lines):
    return [m.group(1).strip() for l in body_lines for m in [re.match(r"^- ([^:\[]+):", l)] if m]


def strip_allowed_brackets(text):
    text = re.sub(r"^## \[DESIGN\] - ", "## ", text, flags=re.M)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"^\s*[-*] \[[ xX]\]", "", text, flags=re.M)
    return text


def common_checks(text, team, kind="standard"):
    found = []
    if team not in TEAMS:
        found.append("team must be %s (build) or %s (UX design), got '%s'" % (TEAMS[0], TEAMS[1], team))
    elif kind == "design" and team != TEAMS[1]:
        found.append("design tickets belong to the %s team, got '%s'" % (TEAMS[1], team))
    if re.search(r"\[[^\]]*\]", strip_allowed_brackets(text)):
        found.append("square brackets remain; replace placeholders with real content, N/A or Nothing")
    for pattern, label in BANNED:
        if re.search(pattern, text, re.I if label == "an update line" else 0):
            found.append("contains %s" % label)
    return found


def check_title_length(title):
    if len(title) > 70:
        return ["title is %d characters; keep it under about 70" % len(title)]
    return []


def check_title(title):
    found = check_title_length(title)
    first = title.split(" ")[0].lower() if title else ""
    if first in NON_VERB_STARTS or not title:
        found.append("title should start with a verb")
    return found


def check_standard(text, kind="standard"):
    found = []
    template = read_template(kind, legacy=(kind == "standard"))
    first = text.strip().splitlines()[0] if text.strip() else ""
    if not first.startswith("## "):
        found.append("first line must be the title as '## <title>'")
    elif kind == "design":
        title = first[3:].strip()
        if not title.startswith(DESIGN_TAG):
            found.append("design ticket title must start with '%s'" % DESIGN_TAG)
        else:
            found += check_title_length(title)
    else:
        found += check_title(first[3:].strip())
    raw = bold_headings(template)
    optional = set(h[len("[Optional] "):] for h in raw if h.startswith("[Optional] "))
    want = [h[len("[Optional] "):] if h.startswith("[Optional] ") else h for h in raw]
    have = bold_headings(text)
    for h in want:
        if h not in have and h not in optional:
            found.append("missing heading: %s" % h)
    extra = [h for h in have if h not in want]
    if extra:
        found.append("extra heading(s): %s" % ", ".join(extra))
    present = [h for h in have if h in want]
    if present != [h for h in want if h in present]:
        found.append("headings are out of order")
    bodies = section_bodies(text)
    tbodies = dict((k[len("[Optional] "):] if k.startswith("[Optional] ") else k, v)
                   for k, v in section_bodies(template).items())
    for h in optional:
        if h in bodies and not any(l.strip() for l in bodies[h]):
            found.append("%s section is empty; add its content or remove the section" % h)
    for name in ("Dependencies", "Potential impacts", "Design references"):
        for label in template_labels(tbodies.get(name, [])):
            lines = [l for l in bodies.get(name, []) if l.startswith("- " + label + ":")]
            value = lines[0].split(":", 1)[1].strip() if lines else ""
            if not value:
                found.append("%s: '%s' needs a value or N/A" % (name, label))
    crit = [l for l in bodies.get("Acceptance criteria", []) if re.match(r"^- \[[ xX]\] \S", l)]
    needed = len([l for l in tbodies.get("Acceptance criteria", []) if l.startswith("- [ ]")])
    if len(crit) < needed:
        found.append("acceptance criteria needs at least %d items, found %d" % (needed, len(crit)))
    joined = " ".join(crit).lower()
    template_wants_must_not = any("must not" in l.lower() for l in tbodies.get("Acceptance criteria", []))
    if template_wants_must_not and "must not" not in joined:
        found.append("acceptance criteria needs an explicit 'Must NOT' exclusion")
    ctx = " ".join(l for l in bodies.get("Business context", []) if l.strip())
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", ctx.strip()) if s]
    if not 1 <= len(sentences) <= 6:
        found.append("Business context must be 1-6 sentences, found %d" % len(sentences))
    if DATED.search(ctx):
        found.append("Business context holds a dated progress note; move it to a dated Linear comment")
    oq = [l[2:].strip() for l in bodies.get("Open questions", []) if l.startswith("- ")]
    if not oq:
        found.append("Open questions needs a real question or 'None'")
    for q in oq:
        found += check_open_question(q)
    return found


NONE_DATED = re.compile(r"^None as of \S.*$")


def check_new_standard(text):
    found = []
    template = read_template("standard")
    first = text.strip().splitlines()[0] if text.strip() else ""
    if not first.startswith("## "):
        found.append("first line must be the title as '## <title>'")
    else:
        found += check_title(first[3:].strip())
    raw = bold_headings(template)
    optional = set(h[len("[Optional] "):] for h in raw if h.startswith("[Optional] "))
    want = [h[len("[Optional] "):] if h.startswith("[Optional] ") else h for h in raw]
    have = bold_headings(text)
    for h in want:
        if h not in have and h not in optional:
            found.append("missing heading: %s" % h)
    extra = [h for h in have if h not in want]
    if extra:
        found.append("extra heading(s): %s" % ", ".join(extra))
    present = [h for h in have if h in want]
    if present != [h for h in want if h in present]:
        found.append("headings are out of order")
    bodies = section_bodies(text)
    for h in optional:
        if h in bodies and not any(l.strip() for l in bodies[h]):
            found.append("%s section is empty; add its content or remove the section" % h)
    ctx = " ".join(l for l in bodies.get("Business context", []) if l.strip())
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", ctx.strip()) if s]
    if not 1 <= len(sentences) <= 3:
        found.append("Business context must be 1-3 sentences, found %d" % len(sentences))
    if DATED.search(ctx):
        found.append("Business context holds a dated progress note; move it to a dated Linear comment")
    reqs = [l for l in bodies.get("Requirements", []) if re.match(r"^- \[[ xX]\] \S", l)]
    if len(reqs) < 2:
        found.append("Requirements needs at least 2 items, found %d" % len(reqs))
    if "Design" in bodies and not any(l.strip() for l in bodies["Design"]):
        found.append("Design needs a link or 'None needed'")
    dep = bodies.get("Dependencies", [])
    waiting = ""
    for label in ("Blocked by", "Waiting on"):
        lines = [l for l in dep if l.startswith("- " + label + ":")]
        if not lines:
            found.append("Dependencies: add a '%s:' line (use Nothing if none)" % label)
            continue
        value = lines[0].split(":", 1)[1].strip()
        if not value:
            found.append("Dependencies: '%s' needs a value or Nothing" % label)
        if label == "Waiting on":
            waiting = value
    oq = [l[2:].strip() for l in bodies.get("Open questions", []) if l.startswith("- ")]
    if not oq:
        found.append("Open questions needs a real question or 'None as of <date>'")
    for q in oq:
        if q.startswith("None"):
            if not NONE_DATED.match(q):
                found.append("Open questions: write 'None as of <date>', not '%s'" % q)
            elif waiting and not re.match(r"^(nothing|none|n/a)\b", waiting.strip().lower()):
                found.append("Open questions says None while Waiting on lists an open decision; list the decision as a question or mark it clearly")
        else:
            found += check_open_question(q)
    return found


def check_open_question(q):
    found = []
    if q != "None" and not q.endswith("?"):
        found.append("Open questions must be 'None' or a question ending in '?': %s" % q)
    if SCOPE_STATEMENT.match(q):
        found.append("Open question is a scope statement; scope lists stay out of the ticket: %s" % q)
    return found


def check_new_epic_sections(section):
    found = []
    if "6" in section:
        body = [l for l in section["6"].splitlines()[1:] if l.strip()]
        if not body:
            found.append("Design references needs a link or 'None needed'")
    if "7" in section:
        for head in ("Decided", "Proposed"):
            if not re.search(r"(?m)^###\s*" + head + r"\s*$", section["7"]):
                found.append("What we know needs a '### %s' list" % head)
        m = re.search(r"(?ms)^###\s*Decided\s*$(.*?)(?=^###|\Z)", section["7"])
        if m and re.search(r"\bproposed\b|\bnot confirmed\b|\bunconfirmed\b", m.group(1), re.I):
            found.append("Decided holds an item that reads as proposed; move it under Proposed")
    if "8" in section:
        lines = [l for l in section["8"].splitlines()[1:] if l.strip()]
        if not lines or not re.match(r"(?i)^as of \S", lines[0].strip()):
            found.append("Readiness summary must start with 'As of <date>'")
    if "9" in section:
        items = [l.strip()[2:].strip() for l in section["9"].splitlines()[1:] if l.strip().startswith("- ")]
        if not items:
            found.append("Open questions needs a real question or 'None as of <date>'")
        for q in items:
            if q.startswith("None"):
                if not NONE_DATED.match(q):
                    found.append("Open questions: write 'None as of <date>', not '%s'" % q)
            else:
                found += check_open_question(q)
    return found


def check_epic(text):
    found = []
    legacy = is_legacy(text, "epic")
    template = read_template("epic", legacy=legacy)
    heads = re.findall(r"^## (\d+)\.\s", text, re.M)
    t_heads = re.findall(r"^## (\d+)\.\s*(\[Optional\])?", template, re.M)
    for num, optional in t_heads:
        if not optional and num not in heads:
            found.append("missing section %s" % num)
    nums = [int(n) for n in heads]
    if nums != sorted(nums):
        found.append("sections are out of order")
    allowed = set(n for n, _ in t_heads)
    for n in heads:
        if n not in allowed:
            found.append("unexpected section %s" % n)
    blocks = re.split(r"^## ", text, flags=re.M)
    section = {}
    for block in blocks[1:]:
        m = re.match(r"(\d+)\.", block)
        if m:
            section[m.group(1)] = block
    if "1" in section:
        body = section["1"].split("\n", 1)[1] if "\n" in section["1"] else ""
        paras = [p for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
        if not 1 <= len(paras) <= 5:
            found.append("Context must be 1-5 short paragraphs, found %d" % len(paras))
        if DATED.search(body):
            found.append("Context holds a dated progress note; move it to a dated Linear comment")
    if "4" in section:
        for line in section["4"].splitlines()[1:]:
            s = line.strip()
            if s and not s.startswith("#") and not STORY.match(s):
                found.append("user story must read '*As a [role], I want to [action], so that [reason].*': %s" % s)
    if "5" in section:
        if "**Acceptance Criteria**" not in section["5"]:
            found.append("section 5 needs an '**Acceptance Criteria**' list")
        if not re.search(r"must not|cannot|can't|can not|not be able|never", section["5"], re.I):
            found.append("section 5 needs an explicit exclusion (what the user or role must not do)")
    extra_sec = "6" if legacy else "10"
    if extra_sec in section:
        for head in re.findall(r"(?m)^#{3,}\s*(.+?)\s*$", section[extra_sec]):
            if SECTION6_BANNED.search(head):
                found.append("section %s may not hold '%s': scope lists and ticket reorganisation proposals stay out of the ticket (future scope that is nice to have is allowed)" % (extra_sec, head))
        m = re.search(r"(?im)^(?:#+\s*|\*\*)Open questions\**\s*$([\s\S]*?)(?=^#|\Z)", section[extra_sec])
        if m:
            for line in m.group(1).splitlines():
                item = line.strip()
                if item.startswith("- "):
                    found += check_open_question(item[2:].strip())
    if not legacy:
        found += check_new_epic_sections(section)
    return found


TICKET_ID = re.compile(r"\b(?:DEV|DES|LEA)-\d+\b")


def ticket_ids(text):
    """Ticket IDs written in the draft, in order of first appearance."""
    seen = []
    for m in TICKET_ID.finditer(text):
        if m.group(0) not in seen:
            seen.append(m.group(0))
    return seen


def check(text, kind, team):
    found = common_checks(text, team, kind)
    if kind == "epic":
        found += check_epic(text)
    elif kind == "standard" and not is_legacy(text, kind):
        found += check_new_standard(text)
    else:
        found += check_standard(text, kind)
    return found


JARGON = ["payload", "schema", "middleware", "refactor", "idempotent", "serialize", "deserialize", "regex", "cron", "latency", "database", "backend", "frontend", "api call", "microservice"]
MAX_LINES = 45


def wording_warnings(text):
    """Plain-language warnings. Printed as WARN lines; they never change the exit status.
    Lines that start with 'Endpoint:' are skipped, because API tickets may name endpoints."""
    warnings = []
    lines = [l for l in text.splitlines() if l.strip()]
    if lines and not lines[0].startswith("## 1.") and len(lines) > MAX_LINES:
        warnings.append("ticket is longer than one screen (%d lines); trim it or make it an epic" % len(lines))
    body = "\n".join(l for l in lines if not l.lower().startswith("endpoint:"))
    seen = []
    for word in JARGON:
        if re.search(r"\b" + re.escape(word) + r"\b", body, re.I) and word not in seen:
            seen.append(word)
    if seen:
        warnings.append("technical wording: %s; say it from the user's point of view" % ", ".join(seen))
    return warnings


def kind_legacy(kind, text):
    return kind in ("standard", "epic") and is_legacy(text, kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["standard", "epic", "design"], required=True)
    ap.add_argument("--team", required=True)
    ap.add_argument("--file", required=True)
    args = ap.parse_args()
    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    problems = check(text, args.kind, args.team)
    for p in problems:
        print("FAIL: " + p)
    if not problems:
        print("OK: draft passes all template checks")
    ids = ticket_ids(text)
    for w in wording_warnings(text):
        print("WARN: " + w)
    if kind_legacy(args.kind, text):
        print("NOTE: this draft uses the old template; new tickets use the current one")
    if ids:
        print("CHECK: ticket IDs in this draft: %s. Confirm none is Done or QA (get_issue) and describe any finished work by name instead." % ", ".join(ids))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
