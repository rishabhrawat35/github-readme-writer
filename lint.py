#!/usr/bin/env python3
"""Check a README against the github-readme-writer rules; exit 1 on any finding.

usage: python3 lint.py <README.md> [--max-body-words 1800] [--min-body-words 150]

Checks: relative links and images exist (markdown, reference-style, HTML
<a href>/<img src>); #anchors match a heading (GitHub rule, incl. -1 -2 for
duplicates and emoji stripping); no unclosed code fence; no placeholders
(<thing>, TODO, TBD, FIXME, lorem, xxx) in prose or commands; no banned filler
words in prose (code spans and code blocks are exempt); a code block in the first
40 lines; a first heading exists; body word count (outside code blocks and
tables) within bounds; a "License" heading exists.

It also fails on eight mechanical AI tells taken from blader/humanizer: a
staged "not just X, it is Y" contrast (NOTXBUTY), an AI vocabulary word
(AIWORD), an inflated-significance phrase (INFLATED), "serves as" where "is"
would do (COPULA), an em dash, en dash or spaced double hyphen outside code
(DASH), chat residue such as "Great question" (RESIDUE), three sentences in a
row opening on the same content word (OPENER), and a one-line paragraph that
restates the heading above it (HEADECHO). Curly quotation marks (CURLY) are the
ninth tell and the one advisory kind: they are printed as a note and never fail
the run.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

BANNED = ["simply", "just", "easy", "easily", "powerful", "seamless", "seamlessly", "robust",
          "cutting-edge", "state-of-the-art", "blazing", "leverage", "leverages", "best-in-class",
          "world-class", "effortless", "effortlessly", "comprehensive", "empower", "empowers", "unlock",
          "delve", "streamline", "streamlines", "elevate", "game-changing", "ensure", "ensures"]
HTML_TAGS = {"a", "abbr", "b", "br", "blockquote", "code", "dd", "del", "details", "div", "dl", "dt",
             "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "ins", "kbd", "li", "ol",
             "p", "picture", "pre", "s", "samp", "small", "source", "span", "strong", "sub",
             "summary", "sup", "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul", "var",
             "video", "center", "font", "u", "tt", "big", "strike", "input", "ruby", "rt", "rp",
             "svg", "path", "g", "rect", "circle", "text", "figure", "figcaption", "caption", "wbr"}
PLACEHOLDER_WORDS = {"thing", "feature", "name", "path", "file", "filename", "repo", "dir", "folder",
                     "url", "slug", "placeholder", "tbd", "command", "arg", "args", "value", "version",
                     "token", "key", "id", "user", "username", "password", "email", "host", "port",
                     "project", "package", "project-name", "your-name", "insert", "description",
                     "org", "owner", "branch", "tag", "date", "n", "x", "y", "number", "text"}
PLACEHOLDER_TEXT = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|lorem ipsum|\bxxx+\b|\[insert [^\]]*\]", re.I)
ANGLE = re.compile(r"<([A-Za-z][A-Za-z0-9_./ -]{0,40})>")
LINK = re.compile(r"\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)", re.M)
HTML_HREF = re.compile(r"<(?:a|img|source|video)\b[^>]*?\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
# A code-block line that is a command the reader is meant to type.
RUNNER = re.compile(r"^(\$ |> |(sudo |uv run |npx |pipx run )?(python3?|node|npm|pnpm|yarn|bun|deno|pip3?|uv|cargo|go|make|just|"
                    r"docker|docker-compose|kubectl|git|gh|claude|codex|gemini|cursor|bash|sh|\./|/[a-z][\w.-]*\b))")

# A line that is a list item, a block quote, an HTML block or a link definition
# is not a plain prose paragraph: OPENER and HEADECHO read prose only, because a
# README's bullets are written in parallel on purpose.
NOT_PROSE = re.compile(r"^\s{0,3}(?:[-*+>]\s|\d+[.)]\s|<|\[[^\]]+\]:)")
# HEADECHO never reads the paragraph under a License heading. The License check
# at the end of this file requires the words "No license yet" when there is no
# LICENSE file, and under the heading "License" that sentence restates the
# heading by construction: the heading names the field and the line gives its
# value. A check that fails the sentence another check in this file demands is
# a defect in the check, so this one pair is exempt. Measured on this
# repository's own README, where it was the only hit of the nine.
HEADECHO_SKIP = re.compile(r"\blicen[cs]e\b", re.I)
# CURLY is the one advisory kind: humanizer marks curly quotes weak alone, and
# most editors auto-curl, so the character is evidence of an editor.
HUM_ADVISORY = {"CURLY"}

# ---------------------------------------------------------------------------
# The nine checks below come from blader/humanizer v3.0.0, MIT. Its 25 patterns
# come from Wikipedia's "Signs of AI writing", maintained by WikiProject AI
# Cleanup, and from reviews of AI-generated text on Wikipedia and elsewhere.
# Only the mechanical half is here: a fixed construction, a lexicon, a
# character class, a count. The judgement half stays in SKILL.md's rule R10 and
# in CHALLENGER.md's R10 row, because no script can see whether a triad has
# three real items or whether a passive sentence hides an actor worth naming,
# and a check that guessed at those would fail the sentences the writer meant.
#
# Every list, regular expression and constant below is a byte-for-byte copy of
# the same block in idea-research/skills/idea-research/lint.py. The two
# repositories ship separately, so each keeps its own copy and the two copies
# must agree word for word. Only the comments and the plumbing that calls
# these are this file's own.
# ---------------------------------------------------------------------------
def mask_prose(line):
    """The line with everything that is not the writer's prose removed.

    Inline code, a URL, a link or image target, a reference-style definition
    and an HTML tag are not prose: the hyphen in `--max-body-words`, in
    `docs/guide.md` and in a badge URL belongs to the flag, the path or the
    URL, and DASH must not read it as a dash. A word inside a URL is the
    site's, not the writer's, so AIWORD does not read one either. Link and alt
    text stay, because the writer wrote those. Every humanizer check reads the
    masked line, so the nine agree on what counts as prose; this is the same
    exemption the banned-word check below already takes by other means.
    """
    s = re.sub(r"`[^`]*`", " ", line)
    s = re.sub(r"<?https?://\S+>?", " ", s)
    s = re.sub(r"^\s{0,3}\[[^\]]+\]:\s*\S+.*$", " ", s)
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return s

def _phrase_re(items):
    """One alternation, longest phrase first, so "enduring legacy" wins over
    "enduring" and one phrase is reported once instead of twice."""
    return re.compile(r"(?<![\w-])(?:%s)(?![\w-])"
                      % "|".join(re.escape(s) for s in sorted(items, key=len, reverse=True)),
                      re.I)

# humanizer 12, plus the single words from 15 and 16. Nine candidates are left
# out, each one for a phrase a README legitimately writes. "robust" and "delve"
# are in BANNED above, so listing them here would report one word twice, and
# "landscape" stays out with them to keep this list identical to the
# idea-research copy. "gate", "gated" and "gating" are technical in a README
# about a checker: "the checker gates the draft" names the machinery. "key" is
# the same case, since a README lists key files and `.env` keys. "actually"
# sits inside the writing rules' own instruction, "say what it actually is".
# "quietly" is the word for a step that fails without saying so. "highlight"
# and "refers to" are scoped by humanizer to one sense each, the verb and the
# definition, and a lexicon cannot tell that sense from the ordinary one in
# "the file it refers to". "boasts" is not here either: it is a COPULA phrase,
# which is where the repair is named, and one word in two lexicons of one file
# is a defect even when the running order hides it.
#
# Every inflection is spelled out as a literal rather than generated, because
# idea-research/skills/idea-research/lint.py holds the same list and the two
# must agree by inspection. The flat list was the bug: "The 2019 launch
# enhanced retention, showcased the funnel, fostered demand and emphasized the
# gap" held four of these words and lit nothing, because only "enhance",
# "showcase", "fostering" and "emphasizing" were listed.
AIWORD = """additionally bolster bolstered bolsters breathtaking crucial crucially emphasize
emphasized emphasizes emphasizing enduring enhance enhanced enhances enhancing exemplifies
exemplify foster fostered fostering fosters garner garnered garners groundbreaking interplay
intricacies intricate meticulous meticulously must-visit nestled pivotal profound renowned
showcase showcased showcases showcasing stunning symbolizing tapestry testament underscore
underscored underscores underscoring valuable vibrant""".split() + [
    "align with", "commitment to", "deep dive", "diverse array", "in the heart of",
    "natural beauty"]
AIWORD_RE = _phrase_re(AIWORD)
# humanizer 13, plus the guess half of 23. The disclaimer half of 23 is left
# out on purpose: a README has to be able to say that a command was not run and
# why, and the writing rules require exactly that sentence, so a check on
# disclaimers would fail the honest marking the procedure asks for.
# humanizer's phrase is "marking or shaping the", so "marking the" and
# "shaping the" are here and the bare "marking a" is not: it fired on "the
# writer ticks each line, marking a file as read", where the word is doing
# ordinary work. "appears to have been" is gone too. It is not on humanizer
# 23's list, and the writing rules mandate that shape of hedge, so a check on
# it failed the honest marking the procedure asks for.
INFLATED = ["stands as a testament", "a pivotal moment", "a crucial moment",
            "plays a key role", "marking the", "shaping the",
            "underscores its importance",
            "reflects a broader", "enduring legacy", "lasting legacy",
            "setting the stage for", "evolving landscape", "indelible mark",
            "continues to thrive", "the future looks bright", "exciting times ahead",
            "a step in the right direction", "it is believed that"]
INFLATED_RE = _phrase_re(INFLATED)
# humanizer 18. "boasts" lands here and only here, because this message names
# the repair and humanizer_words gives each phrase to one check anyway.
COPULA = ["serves as", "stands as", "functions as", "operates as", "represents a",
          "boasts", "features a", "offers a", "maintains a"]
COPULA_RE = _phrase_re(COPULA)
# humanizer 22, the leftovers. "Of course" and "Certainly" carry their
# exclamation mark: without it both are ordinary English. "here is a" and
# "would you like" are anchored to the start of a line for the same reason.
# Mid-sentence they are ordinary too: "Here is a run on this repository, with
# the output it printed" introduces a real output block, which is what Step 4
# demands, and "Every cap here is a ceiling" is ordinary prose. Only the line
# that opens on one is wrapper.
RESIDUE = [(re.compile(r"\bgreat question\b", re.I), "Great question"),
           (re.compile(r"\bi hope this helps\b", re.I), "I hope this helps"),
           (re.compile(r"\bof course\s*!", re.I), "Of course!"),
           (re.compile(r"\bcertainly\s*!", re.I), "Certainly!"),
           (re.compile(u"\\byou(?:['’]?re| are) absolutely right\\b", re.I),
            "You're absolutely right"),
           (re.compile(r"^\s*would you like\b", re.I), "Would you like"),
           (re.compile(r"\bwant me to\b", re.I), "Want me to"),
           (re.compile(r"\bshould i continue\b", re.I), "Should I continue"),
           (re.compile(r"\blet me know\b", re.I), "let me know"),
           (re.compile(r"^\s*here is a\b", re.I), "here is a")]
# humanizer 1. The bare "not X but Y" is NOT here. A README's non-goals are
# written that way on purpose, "It is not a template generator", and this
# repository's own README ships five of them, so a check on the bare form would
# fail the section the writing rules ask for. What is here is the staged form,
# where "just", "only" or "merely" fences off the negative half, and the
# reversed "it is not X, it is Y".
NOTXBUTY_FORMS = (
    (re.compile(u"\\bnot (?:just|only|merely|simply)\\b[^.!?]{1,80}?[,;]?\\s*"
                u"\\b(?:but|it['’]?s|it is)\\b", re.I),
     u'a staged "not just X, it is Y" contrast'),
    (re.compile(u"\\bit(?:['’]s| is) not\\b[^.!?]{1,80}?,\\s*it(?:['’]s| is)\\b", re.I),
     u'an "it is not X, it is Y" contrast'))
# There is no check on the clipped tail, "..., no guessing". Even anchored at
# the end of a sentence it read "One agent, no research." and "Forty clinics
# replied, no doubt." as contrasts, and both are plain English carrying a
# figure. It also ran per line, so it read a wrapped sentence's first half as a
# whole one. It is the weakest form of the pattern, so the reviewer owns it.
# The split contrast is "This does not mean X. It means Y." The bare "This is
# not ..." is gone: that is how a non-goals section opens, and the sentence
# after it is the point rather than the second half of a staged pair.
NOTXBUTY_OPEN = re.compile(u"^(?:this does not mean|this doesn['’]?t mean)\\b", re.I)
NOTXBUTY_SHUT = re.compile(u"^(?:it means|it is|it['’]s)\\b", re.I)
# humanizer 8. The writing rules already forbid em dashes in prose; this makes
# it mechanical. A code fence is skipped by the caller, and inline code, a URL,
# a markdown link target and a file path are masked here, because a hyphen
# inside one of those belongs to the path and not to the writer.
DASH_MASK = re.compile(r"`[^`]*`|https?://\S+|\]\([^)]*\)|(?<!\w)[\w.~]+/[\w./~-]+")
# An en dash between two figures is a range, "700-1,800" written with one, and
# ranges are the one job a comma cannot do, so they are masked too: humanizer 8
# is about the dash used instead of choosing how two clauses relate.
DASH_RANGE = re.compile(u"(?<=\\d)\\s?–\\s?(?=[₹$\\d])")
DASH_FORMS = ((u"—", "an em dash"), (u"–", "an en dash"),
              (" -- ", "a spaced double hyphen"))
# humanizer 21, advisory. Most editors auto-curl, so the character is evidence
# of an editor and not of a machine.
CURLY_CHARS = u"“”‘’"
# The function words and the auxiliaries, copied from the same two lists in the
# idea-research file. OPENER and HEADECHO both read them.
AUX = """is are was were be been being am has have had do does did will would can could should may might must shall ought
need needs cannot isnt arent wasnt werent hasnt havent hadnt dont doesnt didnt wont wouldnt cant couldnt shouldnt
mustnt lets""".split()
CAP_STOP = set("""the this that these those a an and or but so if then it its we you they he she
his her their our your no not do does did there here what which who whom when where why how
for from with without on in at to of by as after before per each every both all only even
because nothing nobody everything someone anyone something anything untried today now still
about into over under again more most less least other another same such than while whether
also just very much many few enough between during within against upon since until though
although unless however therefore thus hence yes maybe never always often sometimes""".split())
# humanizer 7. Two sentences opening on the same word is ordinary English, and
# humanizer says so itself ("She came. She saw. She conquered."); three is the
# rule writing instead of the ear. Except when the repeated word is a function
# word, which is why that sanctioned example sits at exactly three and must
# stay quiet: humanizer 7 says do not ban the repeated word, and "The", "It",
# "She" and "This" are how English starts a sentence about the thing already
# named. "The skill... The reader... The checker..." is this README's own
# opening. So an opener in OPENER_STOP ends the run without reporting it, and
# what is left is three sentences opening on the same content word, which is
# the tell.
OPENER_MIN = 3
OPENER_STOP = CAP_STOP | set(AUX)
FIRST_WORD = re.compile(u"[A-Za-z][A-Za-z'’-]*")
# humanizer 24. Compared on content words, never on the whole string: a heading
# and the sentence under it share their function words whatever either says, so
# a string comparison would have called every opening sentence an echo. One new
# content word is allowed, because "The lab route pays less" under "The lab
# route pays less than the plan assumed" is the tell and one added noun is not.
HEADECHO_MAX_WORDS, HEADECHO_NEW = 12, 1
HEADECHO_STOP = CAP_STOP | set(AUX)

# A run of digits is a content word too, and the most load-bearing one a README
# writes. R9 says numbers replace adjectives, so "The menu holds 38 sections."
# under the heading "Section menu" adds the only thing the heading left out, and
# a letters-only match called it an echo of its own heading.
CONTENT_WORD = re.compile(u"[A-Za-z][A-Za-z'’-]*|\\d[\\d.,%₹]*")

def content_words(text):
    """The words of a heading or a sentence that carry its subject."""
    out = set()
    for w in CONTENT_WORD.findall(text.lower()):
        if w[0].isdigit():
            out.add(w.rstrip(u".,"))
            continue
        w = w.strip(u"'’-")
        if len(w) < 3 or w in HEADECHO_STOP:
            continue
        out.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out

def sentences(text):  return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def humanizer_words(line):
    """INFLATED, COPULA and AIWORD on one line, each phrase reported once.

    The order and the claimed spans are the whole point. "stands as a
    testament" holds a COPULA phrase and an AIWORD inside it, and reporting one
    phrase three times tells the writer nothing the first report did not.
    """
    out, taken = [], []
    for kind, rx, msg in (
            ("INFLATED", INFLATED_RE,
             '"%s" - inflated significance: keep the fact and drop the dressing'),
            ("COPULA", COPULA_RE, '"%s" - write is, are or has'),
            ("AIWORD", AIWORD_RE,
             '"%s" - models reach for this word far more often than people do')):
        for m in rx.finditer(line):
            if any(m.start() < b and a < m.end() for a, b in taken):
                continue
            out.append((kind, msg % m.group(0)))
            taken.append((m.start(), m.end()))
    return out

def humanizer_line(line):
    """The line-scale humanizer checks, as (kind, message) pairs.

    Every one of these reads a line rather than a paragraph, because a README
    puts its claims in a bold lead-in, a table cell and a heading as often as
    in a sentence, and a table row is where a short label most often hides an
    AI word or a dash.

    mask_prose runs FIRST and every check below reads its result, so all nine
    agree on what is the writer's prose: a command, a flag, a path and a badge
    URL are exempt from every one of them and not from DASH alone.
    """
    line = mask_prose(line)
    out, bare, taken = [], line.replace("*", ""), []
    for rx, what in NOTXBUTY_FORMS:
        for m in rx.finditer(bare):
            if any(m.start() < b and a < m.end() for a, b in taken):
                continue
            out.append(("NOTXBUTY", "%s: state the point directly" % what))
            taken.append((m.start(), m.end()))
    out.extend(humanizer_words(line))
    for rx, phrase in RESIDUE:
        if rx.search(line):
            out.append(("RESIDUE", '"%s" is chat wrapper, not an answer: delete it' % phrase))
    masked = DASH_RANGE.sub(" ", DASH_MASK.sub(" ", line))
    for ch, what in DASH_FORMS:
        if ch in masked:
            out.append(("DASH", "%s: use a comma, a colon, a full stop or brackets" % what))
    curly = sum(line.count(c) for c in CURLY_CHARS)
    if curly:
        out.append(("CURLY", "curly quotation marks or apostrophes (%d on this line): "
                    "this README is read as plain text, so write the straight ones" % curly))
    return out

def humanizer_para(sents, head_words, opener=True):
    """The paragraph-scale humanizer checks, as (kind, message) pairs."""
    out = []
    for a, b in zip(sents, sents[1:]):
        if NOTXBUTY_OPEN.match(a) and NOTXBUTY_SHUT.match(b):
            out.append(("NOTXBUTY", 'contrast split across two sentences, "%s" then "%s": '
                        "state the point directly" % (a[:34], b[:26])))
    word, run = None, 0
    for s in (sents + [""]) if opener else []:
        m = FIRST_WORD.search(s.replace("*", ""))
        w = m.group(0).lower() if m else None
        # A function-word opener ends the run without being one: see OPENER_STOP.
        if w in OPENER_STOP:
            w = None
        if w is not None and w == word:
            run += 1
            continue
        if run >= OPENER_MIN:
            out.append(("OPENER", '%d sentences in a row open on "%s": vary the opening '
                        "or merge them" % (run, word)))
        word, run = w, (1 if w else 0)
    if head_words and len(sents) == 1 and len(sents[0].split()) <= HEADECHO_MAX_WORDS:
        said = content_words(sents[0])
        added = said - head_words
        # A figure the heading does not carry is not an echo, whatever the word
        # count says. The one-new-word allowance was calibrated on an added
        # noun, and R9 puts a number above any adjective: "The review runs at
        # most 3 rounds." under "Review rounds" adds the count, which is the one
        # thing a reader of the heading did not have.
        if len(said) >= 2 and len(added) <= HEADECHO_NEW \
                and not any(w[0].isdigit() for w in added):
            out.append(("HEADECHO", "the one sentence under the heading restates it: %s"
                        % sents[0][:60]))
    return out




def gh_anchor(heading: str) -> str:
    """GitHub's heading → anchor rule: lowercase, drop punctuation and emoji, space → '-'."""
    h = re.sub(r"`([^`]*)`", r"\1", heading)          # backticks are removed, content kept
    h = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", h)  # links keep their text
    h = re.sub(r"<[^>]+>", "", h).strip().lower()
    out = []
    for ch in h:
        cat = unicodedata.category(ch)
        if ch in " -_" or cat[0] in "LN":
            out.append(ch)
    return "".join(out).replace(" ", "-")


def is_placeholder(token: str) -> bool:
    t = token.strip().lower().rstrip("/")
    if not t or t.split()[0] in HTML_TAGS or t.startswith(("http", "mailto")) or "@" in t:
        return False  # an HTML tag, an autolink or an e-mail address
    first = t.split()[0]
    return first in PLACEHOLDER_WORDS or first.startswith("your") or any(c in first for c in "/_-")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("readme")
    ap.add_argument("--max-body-words", type=int, default=1800)
    ap.add_argument("--min-body-words", type=int, default=150)
    a = ap.parse_args()
    path = Path(a.readme)
    if not path.is_file():
        sys.exit(f"The path is not a file: {path}")
    root = path.parent
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    findings, advisories = [], []

    # Split prose from code blocks; keep line numbers for messages.
    in_code, fence_mark, fence_line = False, "", 0
    body, code, headings, code_first40 = [], [], [], False
    prose, paras = [], []          # every line outside code; and the plain prose paragraphs
    para, para_line, head_words = [], 0, set()

    def close_para():
        """End a paragraph, and spend the heading above it on that paragraph only."""
        nonlocal para_line, head_words
        if para:
            paras.append((para_line, sentences(" ".join(para)), head_words))
            head_words = set()
        del para[:]

    for i, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if m and (not in_code or line.strip().startswith(fence_mark[0] * len(fence_mark))):
            if not in_code:
                in_code, fence_mark, fence_line = True, m.group(1), i
                if i <= 40:
                    code_first40 = True
                close_para()
                head_words = set()
            else:
                in_code = False
            continue
        if in_code:
            code.append((i, line))
            continue
        prose.append((i, line))    # a heading and a table row are the writer's words too
        h = re.match(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if h:
            headings.append(h.group(2))
            close_para()
            head_words = (set() if HEADECHO_SKIP.search(h.group(2))
                          else content_words(mask_prose(h.group(2))))
        elif not line.strip():
            close_para()
        elif line.strip().startswith("|") or NOT_PROSE.match(line):
            close_para()
            head_words = set()     # a table or a bullet list is not an echo of the heading
        else:
            if not para:
                para_line = i
            para.append(mask_prose(line).strip())
        if line.strip().startswith("|"):
            continue
        body.append((i, line))
    close_para()
    if in_code:
        findings.append(f"A code fence opened at line {fence_line} is never closed; everything after it renders as code.")
    for hm in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", text, re.S | re.I):
        headings.append(re.sub(r"<[^>]+>", "", hm.group(2)).strip())
    if not headings:
        findings.append("The file contains no heading.")
    if not code_first40:
        findings.append("No code block appears in the first 40 lines; the first screen must show a command.")

    body_text = "\n".join(l for _, l in body)
    no_links = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)", r"\1", body_text)
    words = len(re.findall(r"\b\w+\b", no_links))
    if words > a.max_body_words:
        findings.append(f"Body prose is {words} words, above the limit of {a.max_body_words}; move deeper material to docs/.")
    if words < a.min_body_words:
        print(f"Warning: body prose is {words} words, below the minimum of {a.min_body_words}; acceptable for a very small repository, otherwise the reader will lack context.")

    # Anchors, with GitHub's -1, -2 suffixes for duplicate headings.
    anchors, seen = set(), {}
    for h in headings:
        k = gh_anchor(h)
        n = seen.get(k, 0)
        anchors.add(k if n == 0 else f"{k}-{n}")
        seen[k] = n + 1

    def check_target(target: str, where: str):
        target = target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        target = target.replace("\\", "")
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return  # http:, https:, mailto:, tel:, data: …
        if target.startswith("#"):
            if target[1:].lower() not in anchors:
                findings.append(f"{where}: the anchor {target} matches no heading.")
            return
        file_part = target.split("#")[0].split("?")[0]
        p = (root / file_part.lstrip("/")).resolve() if file_part.startswith("/") else (root / file_part).resolve()
        if not p.exists():
            findings.append(f"{where}: the link target does not exist: {target}")

    code_lines = {ln for ln, _ in code}
    noncode = "\n".join("" if i in code_lines else l for i, l in enumerate(lines, 1))  # line numbers preserved
    for rx in (LINK, REF_DEF, HTML_HREF):
        for m in rx.finditer(noncode):
            check_target(m.group(1), f"line {noncode.count(chr(10), 0, m.start()) + 1}")

    # Placeholders: in prose (outside code spans) and inside commands (code blocks).
    for ln, line in body:
        stripped = re.sub(r"`[^`]*`", "", line)
        stripped = re.sub(r"!?\[[^\]]*\]\([^)]*\)", "", stripped)
        for m in PLACEHOLDER_TEXT.finditer(stripped):
            findings.append(f"line {ln}: the placeholder text {m.group(0)!r} remains in prose.")
        for m in ANGLE.finditer(stripped):
            if is_placeholder(m.group(1)):
                findings.append(f"line {ln}: the placeholder {m.group(0)!r} appears in prose; use a real value.")
    for ln, line in code:
        cmd = re.sub(r"\s#.*$", "", line.strip())  # drop a trailing comment
        if not RUNNER.match(cmd):
            continue  # output, file trees and comments may legitimately show <thing>
        for m in ANGLE.finditer(cmd):
            if is_placeholder(m.group(1)):
                findings.append(f"line {ln}: the placeholder {m.group(0)!r} appears in a command; show a realistic argument.")

    # Banned words: whole words, prose only, code spans and link targets exempt.
    for ln, line in body:
        stripped = re.sub(r"`[^`]*`", "", line)
        stripped = re.sub(r"\]\([^)]*\)", "]", stripped)
        stripped = re.sub(r"<[^>]+>", "", stripped)
        for w in BANNED:
            for m in re.finditer(rf"(?<![\w-]){re.escape(w)}(?![\w-])", stripped, re.I):
                ctx = stripped[max(0, m.start() - 25):m.end() + 25].strip()
                findings.append(f"line {ln}: the banned word {w!r} appears in prose: …{ctx}…")

    # The nine humanizer checks. The seven line-scale kinds read every line
    # outside a code block, table rows and headings included, because a README
    # puts its claims in a bold lead-in and a table cell as often as in a
    # sentence; humanizer_line masks each line before reading it. The three
    # that need more than one line read plain prose paragraphs only.
    for ln, line in prose:
        for kind, msg in humanizer_line(line):
            (advisories if kind in HUM_ADVISORY else findings).append(f"line {ln}: {kind}: {msg}")
    for ln, sents, hw in paras:
        for kind, msg in humanizer_para(sents, hw):
            findings.append(f"line {ln}: {kind}: {msg}")

    if not any(re.search(r"\blicen[cs]e\b", h, re.I) for h in headings):
        findings.append("No License heading exists; write 'No license yet' when the repository has no LICENSE file.")

    advisories = list(dict.fromkeys(advisories))
    if advisories:
        print(f"{len(advisories)} advisory note(s) in {path}; these do not fail the run:")
        for adv in advisories:
            print(f"  - {adv}")
    findings = list(dict.fromkeys(findings))
    if findings:
        print(f"{len(findings)} finding(s) in {path}:")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    print(f"OK — {path}: {len(headings)} headings, {words} body words; every link and anchor resolves.")


if __name__ == "__main__":
    main()
