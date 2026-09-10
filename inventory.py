#!/usr/bin/env python3
"""Walk a repository and write readme-inventory.md: every file, nothing skipped.

usage: python3 inventory.py <repo> [--out <path>]

For each file: path, size, kind, first heading / docstring / comment line, and
what it lets a user run (entrypoints). Vendored and generated folders are
listed by name with a file count but not opened. Secret files (.env, keys,
credentials) are listed but their content is never shown. The writer ticks
each line off while reading the repo; an unticked line is a gap in the README.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

# Always skipped: never source. Listed by name with a file count and a sample of names.
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".next", ".cache",
             ".mypy_cache", ".pytest_cache", ".tox", ".idea", ".vscode", ".DS_Store",
             ".ruff_cache", ".gradle", ".terraform", "site-packages", "bower_components"}
# Skipped only when the repo's .gitignore names them; otherwise they are real content
# (workflow-studio keeps its deliverable in build/).
MAYBE_GENERATED = {"dist", "build", "target", "coverage", "out", ".output"}
SECRET_NAMES = re.compile(r"^(\.env(\..*)?|.*\.(pem|key|p12|pfx|jks|keystore)|.*(secret|credential|token)s?.*|"
                          r"id_(rsa|ed25519|ecdsa)|\.npmrc|\.pypirc|\.netrc)$", re.I)
SECRET_ALLOW = re.compile(r"\.(example|sample|template|dist)$", re.I)
TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".txt", ".yaml", ".yml", ".toml",
            ".json", ".sh", ".bash", ".zsh", ".html", ".css", ".sql", ".ini", ".cfg",
            ".env", ".example", ".rst", ".go", ".rs", ".java", ".kt", ".kts", ".rb", ".php",
            ".mjs", ".cjs", ".xml", ".csv", ".mermaid", ".Dockerfile", ".c", ".h", ".cpp",
            ".hpp", ".cs", ".swift", ".scala", ".lua", ".pl", ".r", ".jl", ".ex", ".exs",
            ".gradle", ".mod", ".sum", ".lock", ".conf", ".properties", ".proto", ".graphql",
            ".vue", ".svelte", ".tf", ".ps1", ".bat", ".cmd", ".gitignore", ""}
TEXT_NAMES = {"Makefile", "makefile", "Dockerfile", "LICENSE", "Gemfile", "Rakefile", "Procfile",
              "Justfile", "justfile", "CMakeLists.txt", "go.mod", "go.sum"}
LARGE = 1_000_000  # bytes; flagged so the writer decides whether to open it

# (regex, label, suffixes it applies to; None = any text file)
ENTRY_HINTS = [
    (r"^\s*if __name__ == ['\"]__main__['\"]", "python script (`python3 {p}`)", {".py"}),
    (r"argparse\.ArgumentParser|click\.(command|group)|typer\.Typer|docopt\(", "CLI with flags — run with --help", {".py"}),
    (r"^\s*def main\(", "has main()", {".py"}),
    (r"\bsys\.argv\b", "reads sys.argv", {".py"}),
    (r"=\s*(FastAPI|Flask|express|fastify|Hono)\(|http\.ListenAndServe\(|^use (actix_web|axum)\b", "web server", None),
    (r"^\s*(export\s+)?(async\s+)?function\s+main\b|process\.argv|yargs|commander", "node script", {".js", ".mjs", ".cjs", ".ts"}),
    (r"^package main\b[\s\S]*^func main\(", "go program (`go run .` in its folder)", {".go"}),
    (r"^\s*(pub\s+)?(async\s+)?fn main\(", "rust binary (`cargo run`)", {".rs"}),
    (r"public\s+static\s+void\s+main\s*\(", "java main class", {".java"}),
    (r"^\s*fun main\(", "kotlin main", {".kt", ".kts"}),
    (r"static\s+(async\s+)?(void|int|Task)\s+Main\s*\(", "C# entry", {".cs"}),
    (r"^\s*int\s+main\s*\(", "C/C++ program", {".c", ".cpp"}),
    (r"if __FILE__ == \$0|\$PROGRAM_NAME", "ruby script", {".rb"}),
    (r"^#!", "executable script (shebang)", {".sh", ".bash", ".zsh", ".pl", ".rb", ".py", ".js", ""}),
]
ENTRY_HINTS = [(re.compile(rx, re.M), label, ext) for rx, label, ext in ENTRY_HINTS]

MANIFESTS = {
    "pyproject.toml": "python project (deps + maybe [project.scripts] CLI)", "setup.py": "python deps",
    "setup.cfg": "python deps", "requirements.txt": "python deps", "Pipfile": "python deps",
    "environment.yml": "conda env", "uv.lock": "python lockfile", "poetry.lock": "python lockfile",
    "package.json": "node project", "Cargo.toml": "rust crate (`cargo run`/`cargo build`)",
    "go.mod": "go module (`go run .`/`go build`)", "pom.xml": "java (maven)",
    "build.gradle": "java/kotlin (gradle)", "build.gradle.kts": "kotlin (gradle)",
    "Gemfile": "ruby deps", "composer.json": "php deps", "Package.swift": "swift package",
    "CMakeLists.txt": "C/C++ (cmake)", "mix.exs": "elixir project", "Justfile": "just recipes",
    "justfile": "just recipes", "Procfile": "process entry", "Taskfile.yml": "task runner",
    "Vagrantfile": "vagrant", "flake.nix": "nix flake", "action.yml": "GitHub Action",
    "pubspec.yaml": "dart/flutter", "deno.json": "deno", "bun.lockb": "bun",
}


def is_text(path: Path, head: bytes) -> bool:
    if b"\x00" in head:
        return False
    if path.suffix.lower() in TEXT_EXT or path.name in TEXT_NAMES:
        return True
    try:
        head.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def summarize(path: Path, text: str) -> str:
    """One line that says what the file is, from its own words."""
    suf = path.suffix.lower()
    if suf == ".py":
        m = re.search(r'^\s*(?:[rub]*"""|[rub]*\'\'\')\s*(.+?)\s*$', text, re.M)
        if m:
            return m.group(1).strip("\"' ")
    if suf in {".md", ".rst", ".mdx"}:
        fm = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
        if fm:
            d = re.search(r"^description:\s*['\"]?(.+?)['\"]?\s*$", fm.group(1), re.M)
            if d:
                return d.group(1)
            n = re.search(r"^(name|title):\s*['\"]?(.+?)['\"]?\s*$", fm.group(1), re.M)
            if n:
                return n.group(2)
        h = re.search(r"^#{1,3}\s+(.+?)\s*#*\s*$", text, re.M)
        if h:
            return h.group(1)
        t = re.search(r"<title>(.*?)</title>|<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
        if t:
            return re.sub(r"<[^>]+>", "", t.group(1) or t.group(2)).strip()
    if suf == ".json":
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                for k in ("description", "name", "title", "$schema"):
                    if isinstance(obj.get(k), str):
                        return f"{k}: {obj[k]}"
        except ValueError:
            pass
    if suf == ".html":
        t = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
        if t:
            return t.group(1).strip()
    if suf in {".yaml", ".yml", ".toml"}:
        d = re.search(r"^(description|name|title)\s*[:=]\s*['\"]?(.+?)['\"]?\s*$", text, re.M)
        if d:
            return f"{d.group(1)}: {d.group(2)}"
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#!", "---", "<!--", "*/", "import ", "from ", "package ", "use ",
                                  "{", "}", "[", "]", "<", "@")):
            continue
        s = re.sub(r"^(//[/!]?|/\*+|\*|#+|--|;+|%+|\"\"\"|''')\s*", "", s)
        s = re.sub(r"\s*(\*/|-->)\s*$", "", s).strip()
        if s:
            return s
    return ""


def read_text(path: Path, size: int):
    """Return (text or None, note). None means: binary or secret, not read."""
    if not SECRET_ALLOW.search(path.name) and SECRET_NAMES.match(path.name):
        return None, "SECRET — listed, not read; never copy into a README"
    try:
        with open(path, "rb") as f:
            head = f.read(min(size, 200_000))
    except OSError as e:
        return None, f"unreadable ({e.strerror})"
    if not is_text(path, head):
        return None, ""
    try:
        return head.decode("utf-8"), ""
    except UnicodeDecodeError:
        return head.decode("utf-8", errors="replace"), "not valid UTF-8"


def office_title(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if "docProps/core.xml" in names:
                core = z.read("docProps/core.xml").decode("utf-8", errors="replace")
                m = re.search(r"<dc:title>(.*?)</dc:title>", core, re.S)
                if m and m.group(1).strip():
                    return "title: " + m.group(1).strip()
            if path.suffix.lower() == ".xlsx" and "xl/workbook.xml" in names:
                wb = z.read("xl/workbook.xml").decode("utf-8", errors="replace")
                sheets = re.findall(r'<sheet [^>]*name="([^"]+)"', wb)
                if sheets:
                    return "sheets: " + ", ".join(sheets[:8])
            if path.suffix.lower() == ".pptx":
                n = sum(1 for x in names if re.match(r"ppt/slides/slide\d+\.xml$", x))
                return f"{n} slides"
    except (OSError, zipfile.BadZipFile, KeyError):
        pass
    return ""


def special(path: Path, rel: str, text):
    name = path.name
    notes = []
    if name == "package.json":
        try:
            pkg = json.loads(path.read_text(encoding="utf-8"))
            if pkg.get("bin"):
                b = pkg["bin"]
                notes.append("npm bin: " + (", ".join(f"`{k}`" for k in b) if isinstance(b, dict) else f"`{b}`"))
            scripts = pkg.get("scripts", {})
            if scripts:
                notes.append("npm scripts: " + ", ".join(f"`{k}`" for k in scripts))
            if pkg.get("workspaces"):
                notes.append("npm workspaces (monorepo)")
        except (OSError, ValueError):
            notes.append("package.json (unreadable)")
    elif name in MANIFESTS:
        notes.append(MANIFESTS[name])
    if name in {"Makefile", "makefile", "Justfile", "justfile"} and text is not None:
        targets = [t for t in re.findall(r"^([a-zA-Z0-9_][a-zA-Z0-9_.\-/]*)\s*:(?!=)", text, re.M)
                   if not t.startswith(".")]
        if targets:
            notes.append(f"{'make' if 'ake' in name else 'just'} targets: " + ", ".join(f"`{t}`" for t in dict.fromkeys(targets)))
    if name.startswith("Dockerfile") or name.endswith(".Dockerfile") or name in {"docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml"}:
        notes.append("container entry")
    if rel.startswith((".github/workflows/", ".gitlab-ci", ".circleci/")) or name in {"Jenkinsfile", ".travis.yml", "azure-pipelines.yml"}:
        notes.append("CI workflow")
    if name in {".env.example", ".env.sample", ".env.template", "env.example"}:
        notes.append("env vars the user must set")
    if name in {"SKILL.md", "AGENTS.md", "CLAUDE.md", ".cursorrules", "GEMINI.md"} or rel.startswith(".claude/"):
        notes.append("agent instructions")
    if re.search(r"(^|/)(commands|skills|prompts|agents)/", rel):
        notes.append("command/skill template")
    if re.search(r"(^|/)(tests?|__tests__|spec|specs|fixtures)/|(^|/)(test_[^/]+|[^/]+_test|[^/]+\.test|[^/]+\.spec)\.[a-z]+$", rel):
        notes.append("test/fixture — shows real use and expected output")
    if name.lower() == "license" or name.lower().startswith(("license.", "licence")):
        notes.append("LICENSE present")
    if name.lower() in {"readme.md", "readme.rst", "readme.txt", "readme"} and text is not None:
        notes.append(f"existing README, {len(text.split())} words — keep a copy before rewriting")
    return notes


def kind(path: Path, text) -> str:
    ext = path.suffix.lower()
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp"}:
        return "image"
    if ext in {".docx", ".xlsx", ".pptx", ".dotx", ".xlsm"}:
        return "office"
    if ext in {".pdf", ".zip", ".gz", ".tar", ".bin", ".pyc", ".so", ".dylib", ".dll", ".exe",
               ".mp4", ".mp3", ".wav", ".woff", ".woff2", ".ttf", ".parquet", ".sqlite", ".db"}:
        return "binary"
    return "text" if text is not None else "binary"


def gitignored(root: Path):
    try:
        raw = (root / ".gitignore").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return {ln.strip().strip("/").split("/")[-1] for ln in raw.splitlines()
            if ln.strip() and not ln.startswith("#")}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo")
    ap.add_argument("--out", default=None, help="default: <repo>/readme-inventory.md")
    a = ap.parse_args()
    root = Path(a.repo).resolve()
    if not root.exists():
        sys.exit(f"does not exist: {root}")
    if not root.is_dir():
        sys.exit(f"not a directory (pass the repo folder, not a file): {root}")
    out = Path(a.out) if a.out else root / "readme-inventory.md"
    ignored = gitignored(root)

    files, links, skipped, unreadable = [], [], [], []

    def walk(d: Path):
        try:
            entries = sorted(d.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError as e:
            unreadable.append((d.relative_to(root).as_posix(), e.strerror))
            return
        for p in entries:
            rel = p.relative_to(root).as_posix()
            if rel == out.name and p.parent == out.parent:
                continue  # our own output
            if p.is_symlink():
                try:
                    target = p.resolve(strict=True)
                    links.append((rel, target.relative_to(root).as_posix() if root in target.parents or target == root else str(target), True))
                except (OSError, RuntimeError):
                    links.append((rel, str(p.readlink()) if hasattr(p, "readlink") else "?", False))
                continue  # never follow: loops and duplicates
            if p.is_dir():
                if p.name in SKIP_DIRS or (p.name in MAYBE_GENERATED and p.name in ignored):
                    names = [q.relative_to(p).as_posix() for q in p.rglob("*") if q.is_file()]
                    skipped.append((rel, len(names), names[:5]))
                else:
                    walk(p)
            elif p.is_file():
                files.append(p)

    walk(root)

    lines = [f"# Inventory of `{root.name}`", "",
             "Tick every line as you read the file. An unticked line is a gap in the README.", ""]
    if not files and not skipped and not links:
        lines += ["**The folder is empty.** There is nothing to document; tell the owner.", ""]

    # Top-level map first, so a monorepo can be split into passes without losing count.
    top = {}
    for p in files:
        rel = p.relative_to(root)
        key = rel.parts[0] + "/" if len(rel.parts) > 1 else "(root)"
        top[key] = top.get(key, 0) + 1
    if len(files) > 40:
        lines += ["## By top-level folder", ""] + [f"- `{k}` — {n} files" for k, n in sorted(top.items(), key=lambda kv: -kv[1])] + [""]
        if len(files) > 1500:
            lines += [f"**Large repo ({len(files)} files).** Work folder by folder from the map above; "
                      "do not sample. If the repo is a monorepo, one README per package plus a root README that routes.", ""]

    lines += ["## Files", ""]
    deps, total_bytes, secrets = set(), 0, []
    for p in files:
        rel = p.relative_to(root).as_posix()
        try:
            size = p.stat().st_size
        except OSError as e:
            lines.append(f"- [ ] `{rel}` (unreadable: {e.strerror})")
            continue
        total_bytes += size
        text, note = read_text(p, size)
        k = kind(p, text)
        notes = [note] if note else []
        if note.startswith("SECRET"):
            secrets.append(rel)
            k = "secret"
        summary = ""
        if text is not None:
            summary = summarize(p, text)
            hints = [label.format(p=rel) for rx, label, exts in ENTRY_HINTS
                     if (exts is None or p.suffix.lower() in exts or (p.suffix == "" and "" in exts)) and rx.search(text)]
            if hints:
                notes.append("; ".join(dict.fromkeys(hints)))
            if p.suffix == ".py":
                for m in re.finditer(r"^\s*(?:import|from)\s+([a-zA-Z_]\w*)", text, re.M):
                    deps.add(m.group(1))
        elif k == "office":
            summary = office_title(p)
            notes.append("office document — convert to text to read it (e.g. pandoc, python-docx/openpyxl)")
        if size >= LARGE:
            notes.append(f"large ({size/1e6:.1f} MB) — decide whether the user must know about it")
        notes += special(p, rel, text)
        desc = " — ".join(x for x in [summary[:110], "; ".join(dict.fromkeys(notes))] if x)
        lines.append(f"- [ ] `{rel}` ({size:,} B, {k}){' — ' + desc if desc else ''}")

    if links:
        lines += ["", "## Symlinks (listed, not followed)", ""]
        lines += [f"- [ ] `{rel}` → `{tgt}`" + ("" if ok else " — **broken**") for rel, tgt, ok in links]
    if unreadable:
        lines += ["", "## Could not list", ""] + [f"- `{rel}/` — {err}" for rel, err in unreadable]

    lines += ["", "## Not opened (vendored / generated)", ""]
    lines += [f"- `{rel}/` — {n} files" + (f" (e.g. {', '.join('`'+x+'`' for x in ex)})" if ex else "")
              for rel, n, ex in skipped] or ["- none"]
    if secrets:
        lines += ["", "## Secret files (never quote their content; document only that they must exist)", ""]
        lines += [f"- `{s}`" for s in secrets]
    stdlib_guess = set(getattr(sys, "stdlib_module_names", ())) | {
        "os", "sys", "re", "json", "pathlib", "argparse", "subprocess", "typing", "datetime",
        "collections", "itertools", "functools", "shutil", "tempfile", "time", "math", "io",
        "textwrap", "hashlib", "dataclasses", "enum", "copy", "glob", "string", "unittest",
        "logging", "random", "csv", "urllib", "http", "html", "xml", "sqlite3", "threading",
        "concurrent", "asyncio", "contextlib", "operator", "statistics", "difflib", "fnmatch",
        "importlib", "inspect", "traceback", "signal", "socket", "struct", "base64", "uuid",
        "zipfile", "tarfile", "gzip", "pprint", "queue", "select", "platform", "getpass",
        "warnings", "abc", "types", "numbers", "decimal", "fractions", "secrets", "tomllib",
        "zoneinfo", "calendar", "locale", "codecs", "unicodedata", "heapq", "bisect", "array",
        "weakref", "gc", "atexit", "errno", "stat", "filecmp", "shlex", "cmd", "pdb", "timeit",
        "ast", "dis", "tokenize", "keyword", "builtins", "__future__"}
    local = {p.stem for p in files if p.suffix == ".py"} | {p.name for p in files if (p / "__init__.py").exists()}
    local |= {q.parent.name for q in files if q.name == "__init__.py"}
    third = sorted(d for d in deps if d not in stdlib_guess and d not in local)
    lines += ["", "## Python imports that are not stdlib (verify each is declared)", "",
              ", ".join(f"`{d}`" for d in third) if third else "none"]
    lines += ["", f"Total: {len(files)} files, {total_bytes:,} bytes listed; {len(links)} symlinks; "
              f"{len(skipped)} folders not opened; {len(secrets)} secret files not read."]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    extra = f", {sum(1 for l in links if not l[2])} broken symlink(s)" if any(not l[2] for l in links) else ""
    try:
        shown = out.resolve().relative_to(Path.cwd())
    except ValueError:
        shown = out
    print(f"wrote {shown} ({len(files)} files listed, {len(skipped)} folders skipped{extra})")


if __name__ == "__main__":
    main()
