#!/usr/bin/env bash
# -*- mode: python -*-
# Polyglot: re-exec inside `nix develop` so all dependencies are available
# without the caller needing to enter the dev shell manually.
''':'
exec nix --extra-experimental-features "nix-command flakes" develop --command python3 "$0" "$@"
'''

"""
OSGeo Content Verifier
======================

Cross-checks the local Hugo content/ tree against the canonical osgeo.org
website. For each endpoint listed in osgeo.org's page sitemap (plus any
locally harvested pages), it fetches the upstream HTML, normalises both
sides to a plain word stream (disregarding markup, structural logic,
whitespace and punctuation) and compares them word-for-word.

A summary table lists each endpoint together with its check state:

  match            -- word streams are identical
  diff             -- word streams differ (similarity ratio + first divergence shown)
  missing-local    -- upstream page has no local equivalent
  missing-remote   -- local file (harvested_from:) URL no longer in sitemap
  excepted         -- endpoint is in the exception list (skipped)
  error            -- network / parse error

Exception list:
  scripts/verify_exceptions.json -- managed independently of the harvester.
  Pages in here are reported as `excepted` and otherwise ignored.

Link integrity:
  Unless --skip-links is passed, every hyperlink inside the local markdown
  files is extracted, classified (internal-absolute / internal-relative /
  external / anchor / mailto), and HEAD-checked over HTTP.  Pages with any
  broken link are flagged in the report.  Use --remap-internal to rewrite
  legacy `https://www.osgeo.org/...` URLs in your markdown files to the
  Hugo-relative `/...` form so they keep working under the new URL scheme.

In addition to verification, the script can emit an nginx redirect map
that forwards every legacy WordPress URL (the upstream path in the sitemap)
to its new Hugo URL. Use --nginx-config PATH to write the config. The file
is suitable for inclusion via `include /etc/nginx/snippets/osgeo-redirects.conf;`
inside the server { } block.

Usage:
  python3 scripts/verify_content.py [--verbose] [--output table|markdown|json]
                                    [--exceptions PATH] [--threshold 0.95]
                                    [--filter REGEX] [--limit N]
                                    [--save PATH] [--nginx-config PATH]
                                    [--skip-links] [--remap-internal]
                                    [--link-workers N] [--link-timeout SECONDS]
"""

import argparse
import concurrent.futures
import difflib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from urllib.parse import urlparse, urljoin, urlunparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _find_site_root() -> Path:
    """Locate the Hugo project root.

    Priority:
      1. $OSGEO_HUGO_ROOT environment variable
      2. Walk up from CWD looking for `config.toml` (Hugo project marker)
      3. Fall back to two levels up from this script
    """
    env = os.environ.get("OSGEO_HUGO_ROOT")
    if env:
        return Path(env).resolve()
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / "config.toml").is_file():
            return parent
    return Path(__file__).resolve().parent.parent


SITE_ROOT = _find_site_root()
CONTENT_DIR = SITE_ROOT / "content"
EXCEPTION_LIST_FILE = SITE_ROOT / "scripts" / "verify_exceptions.json"
LINK_FIXES_FILE = SITE_ROOT / "scripts" / "link_fixes.json"
PAGE_SITEMAP_URL = "https://www.osgeo.org/page-sitemap.xml"
BASE_URL = "https://www.osgeo.org"
REQUEST_DELAY = 0.4  # seconds between page fetches, be polite

# Hostnames we treat as "internal" (osgeo.org). Links pointing at these are
# candidates for remapping to Hugo-relative URLs.
INTERNAL_HOSTS = {"osgeo.org", "www.osgeo.org"}

# User-Agent used for every outbound request.
USER_AGENT = "OSGeo-Hugo-Verifier/1.0 (content/link integrity)"

console = Console()


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

@dataclass
class LinkCheck:
    """One link occurrence inside a local page."""
    page_url: str         # the Hugo page that contains this link
    raw_url: str          # link target as it appears in the markdown source
    resolved: str         # absolute URL that will actually be HTTP-checked
    kind: str             # internal-absolute|internal-relative|external|anchor|mailto|other
    ok: bool | None = None    # None = not network-checked (anchor/mailto/other)
    status: str = ""          # HTTP status code or short error class
    remap_to: str = ""        # Hugo-relative URL to rewrite raw_url to (if applicable)
    fix_id: str = ""          # id from link_fixes.json applied to this URL (empty if none)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CheckResult:
    url: str
    state: str  # match | diff | empty | missing-local | missing-remote | excepted | error
    similarity: float | None = None
    remote_words: int = 0
    local_words: int = 0
    detail: str = ""
    local_path: str = ""
    hugo_url: str = ""        # URL the local file will be served at by Hugo
    link_total: int = 0       # total link occurrences scanned on this page
    link_checked: int = 0     # number actually HTTP-checked
    link_broken: int = 0      # number that came back as broken
    link_remap_pending: int = 0  # internal-absolute links that should be rewritten
    link_fixes_applied: int = 0  # link_fixes.json substitutions used on this page

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.similarity is not None:
            d["similarity"] = round(self.similarity, 4)
        return d


# ---------------------------------------------------------------------------
# Exception list
# ---------------------------------------------------------------------------

def load_exception_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list of URL paths")
    return [str(x) for x in data]


# ---------------------------------------------------------------------------
# Link fixes registry
# ---------------------------------------------------------------------------

LinkFix = tuple[str, re.Pattern, str]  # (id, compiled_pattern, replacement)


def load_link_fixes(path: Path = LINK_FIXES_FILE) -> list[LinkFix]:
    """Load the URL-rewrite registry. Returns a list of (id, pattern, repl)."""
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    fixes: list[LinkFix] = []
    for entry in data.get("fixes", []):
        try:
            fixes.append((
                entry["id"],
                re.compile(entry["pattern"]),
                entry["replacement"],
            ))
        except (KeyError, re.error) as e:
            console.print(f"[red]Skipping malformed link fix:[/red] {entry} ({e})")
    return fixes


def apply_link_fix(url: str, fixes: list[LinkFix]) -> tuple[str, str]:
    """Try each fix in order. Returns (new_url, fix_id) or (url, '')."""
    for fix_id, pat, repl in fixes:
        new = pat.sub(repl, url)
        if new != url:
            return new, fix_id
    return url, ""


def normalise_path(path: str) -> str:
    """Normalise a URL path: leading slash, trailing slash, no double slashes."""
    if not path:
        return "/"
    path = "/" + path.strip("/")
    return path + "/" if path != "/" else "/"


def is_excepted(path: str, exceptions: list[str]) -> bool:
    norm = normalise_path(path)
    return any(normalise_path(p) == norm for p in exceptions)


# ---------------------------------------------------------------------------
# Sitemap fetching
# ---------------------------------------------------------------------------

def fetch_sitemap_urls(sitemap_url: str = PAGE_SITEMAP_URL) -> list[str]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    resp = requests.get(sitemap_url, timeout=20, headers={
        "User-Agent": "OSGeo-Hugo-Verifier/1.0"
    })
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    urls = []
    for url_el in root.findall("s:url", ns):
        loc = url_el.find("s:loc", ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls


# ---------------------------------------------------------------------------
# Local content discovery
# ---------------------------------------------------------------------------

HARVESTED_RE = re.compile(r'^harvested_from:\s*["\']?([^"\'\n]+)["\']?\s*$', re.MULTILINE)


def discover_local_pages() -> dict[str, Path]:
    """Map normalised URL path -> local markdown file for every file that
    carries a `harvested_from:` front-matter key."""
    mapping: dict[str, Path] = {}
    for md_file in CONTENT_DIR.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        m = HARVESTED_RE.search(text)
        if not m:
            continue
        url = m.group(1).strip()
        path = urlparse(url).path or "/"
        mapping[normalise_path(path)] = md_file
    return mapping


def local_path_to_hugo_url(path: Path) -> str:
    """Derive the URL Hugo will serve a content file at.

    Examples:
      content/_index.md             -> /
      content/about/_index.md       -> /about/
      content/about/board/index.md  -> /about/board/
      content/foo.md                -> /foo/

    This does not consult front-matter `url:` or `slug:` overrides; for the
    osgeo.org migration those are not used by the harvested pages.
    """
    try:
        rel = path.relative_to(CONTENT_DIR)
    except ValueError:
        return ""
    parts = list(rel.parts)
    last = parts[-1]
    if last in {"_index.md", "index.md"}:
        parts = parts[:-1]
    else:
        # leaf .md file -> drop extension, becomes its own URL segment
        parts[-1] = Path(last).stem
    return "/" + "/".join(parts) + ("/" if parts else "")


def url_to_candidate_paths(url_path: str) -> list[Path]:
    """Return candidate local paths for a URL when no harvested_from match
    exists. Mirrors the harvester's url_to_content_path logic but returns
    a list because we don't know whether it's a section or leaf."""
    p = url_path.strip("/")
    if not p:
        return [CONTENT_DIR / "_index.md"]
    candidates = [
        CONTENT_DIR / p / "_index.md",
        CONTENT_DIR / p / "index.md",
        CONTENT_DIR / f"{p}.md",
    ]
    return candidates


# ---------------------------------------------------------------------------
# HTML fetch + text extraction
# ---------------------------------------------------------------------------

def fetch_remote_text(url: str) -> str:
    """Fetch a page and return its main-content plain text."""
    resp = requests.get(url, timeout=30, headers={
        "User-Agent": "OSGeo-Hugo-Verifier/1.0"
    })
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    container = (
        soup.find("div", class_="entry-content")
        or soup.find("article")
        or soup.find("main")
        or soup.find("div", id="content")
        or soup.body
    )
    if container is None:
        return ""
    for tag in container.find_all(["nav", "aside", "footer", "script", "style", "form"]):
        tag.decompose()
    for tag in container.find_all("div", class_=re.compile(
        r"sharedaddy|jp-relatedposts|post-navigation|social-share|breadcrumb"
    )):
        tag.decompose()
    return container.get_text(separator=" ", strip=True)


FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
SHORTCODE_RE = re.compile(r"\{\{[<>%].*?[%>]\}\}", re.DOTALL)
HTML_TAG_RE = re.compile(r"<[^>]+>")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
MD_CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
MD_INLINE_CODE_RE = re.compile(r"`[^`]+`")


def markdown_to_text(md: str) -> str:
    """Strip Hugo front matter, shortcodes, and markdown syntax to plain text."""
    md = FRONT_MATTER_RE.sub("", md, count=1)
    md = MD_CODE_BLOCK_RE.sub(" ", md)
    md = MD_INLINE_CODE_RE.sub(" ", md)
    md = SHORTCODE_RE.sub(" ", md)
    md = MD_IMAGE_RE.sub(" ", md)
    md = MD_LINK_RE.sub(r"\1", md)
    md = HTML_TAG_RE.sub(" ", md)
    return md


# ---------------------------------------------------------------------------
# Word-stream comparison
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"[A-Za-z0-9À-ɏͰ-ϿЀ-ӿ]+")


def to_word_stream(text: str) -> list[str]:
    """Lower-case, strip punctuation/markup, return list of words.

    Disregards all whitespace and structural logic -- only the running
    sequence of word tokens matters.
    """
    return [w.lower() for w in WORD_RE.findall(text)]


def compare_word_streams(remote: list[str], local: list[str]) -> tuple[float, str]:
    """Return (similarity_ratio, divergence_detail)."""
    if not remote and not local:
        return 1.0, ""
    sm = difflib.SequenceMatcher(a=remote, b=local, autojunk=False)
    ratio = sm.ratio()

    # Find first non-equal opcode to describe where they diverge.
    detail = ""
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        sample_remote = " ".join(remote[i1:min(i2, i1 + 6)]) or "(empty)"
        sample_local = " ".join(local[j1:min(j2, j1 + 6)]) or "(empty)"
        detail = (
            f"first diff @ word #{i1}: "
            f"upstream='{sample_remote}' vs local='{sample_local}'"
        )
        break
    return ratio, detail


# ---------------------------------------------------------------------------
# Hyperlink extraction, classification, remapping, checking
# ---------------------------------------------------------------------------

# Markdown link forms we care about:
#   [text](url)        regular link
#   [text](url "...")  link with title
#   [text](<url>)      angle-bracket URL form (allows ()/spaces inside url)
#   <https://url>      autolink
#   [ref]: url         reference definition
#
# URLs may contain `(` / `)` if they are backslash-escaped (CommonMark). The
# inner character class therefore accepts `\(` and `\)` as URL characters,
# otherwise stopping at the unescaped `)` that closes the markdown link.
# Code blocks are removed up-front to avoid pulling URLs from sample code.
_URL_CHAR = r"(?:\\[()]|[^\s()<>])"
MD_LINK_TARGET_RE = re.compile(
    # Angle-bracket form first so its URL can contain unescaped parens/spaces.
    r'\[(?:[^\]]+)\]\(\s*<([^>]+)>(?:\s+"[^"]*")?\s*\)'
    r'|'
    r'\[(?:[^\]]+)\]\(\s*(' + _URL_CHAR + r'+)(?:\s+"[^"]*")?\s*\)'
)
MD_AUTOLINK_RE = re.compile(r"<((?:https?|ftp)://[^>\s]+)>")
MD_REF_DEF_RE = re.compile(
    r"^\s{0,3}\[(?:[^\]]+)\]:\s*<?([^\s>]+)>?", re.MULTILINE
)


_MD_ESCAPED_PAREN_RE = re.compile(r"\\([()])")


def _unescape_md_url(url: str) -> str:
    """Undo CommonMark backslash-escapes for parens inside a URL.

    `\\(` -> `(`, `\\)` -> `)`. html2text often emits these unnecessarily
    inside angle-bracket URLs (where parens don't need escaping), which then
    causes reachability checks against e.g. Wikipedia to 404.
    """
    return _MD_ESCAPED_PAREN_RE.sub(r"\1", url)


def _md_link_iter(text: str):
    """Yield link target strings from MD_LINK_TARGET_RE matches.

    The regex has two alternatives; we pick whichever group matched.
    """
    for m in MD_LINK_TARGET_RE.finditer(text):
        yield m.group(1) or m.group(2)


def extract_links_from_markdown(md: str) -> list[str]:
    """Return every link target found inside `md`, in document order.

    Code blocks and inline code are stripped so example URLs in code do not
    pollute the results.
    """
    cleaned = MD_CODE_BLOCK_RE.sub(" ", md)
    cleaned = MD_INLINE_CODE_RE.sub(" ", cleaned)
    # Strip Hugo front-matter so YAML "aliases:" entries are not picked up
    # as links.
    cleaned = FRONT_MATTER_RE.sub("", cleaned, count=1)
    links: list[str] = []
    links.extend(_md_link_iter(cleaned))
    links.extend(MD_AUTOLINK_RE.findall(cleaned))
    links.extend(MD_REF_DEF_RE.findall(cleaned))
    return links


def classify_link(raw_url: str) -> str:
    """Return a short kind string describing what sort of link this is."""
    if not raw_url:
        return "other"
    s = raw_url.strip()
    if s.startswith("#"):
        return "anchor"
    low = s.lower()
    if low.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return "mailto"
    parsed = urlparse(s)
    if not parsed.scheme and not parsed.netloc:
        return "internal-relative"
    if parsed.scheme not in ("http", "https", "ftp"):
        return "other"
    if parsed.netloc.lower() in INTERNAL_HOSTS:
        return "internal-absolute"
    return "external"


def remap_internal_to_hugo(raw_url: str) -> str:
    """Rewrite an internal-absolute osgeo.org URL to a Hugo-relative path.

    https://www.osgeo.org/about/board/?foo=1#x -> /about/board/?foo=1#x
    Anything that isn't an internal-absolute URL is returned unchanged.
    """
    if classify_link(raw_url) != "internal-absolute":
        return raw_url
    parsed = urlparse(raw_url)
    path = parsed.path or "/"
    new = path
    if parsed.query:
        new += "?" + parsed.query
    if parsed.fragment:
        new += "#" + parsed.fragment
    return new


def resolve_for_checking(raw_url: str, page_hugo_url: str) -> str | None:
    """Return an absolute URL we can HEAD-check, or None if not checkable.

    `page_hugo_url` is used as the base for relative paths. Markdown
    backslash-escapes of parens are removed before the URL is returned so
    that html2text artefacts (e.g. `https://en.wikipedia.org/wiki/501\\(c\\)_organization`)
    do not falsely look broken.
    """
    raw_url = _unescape_md_url(raw_url)
    kind = classify_link(raw_url)
    if kind in ("anchor", "mailto", "other"):
        return None
    if kind == "internal-relative":
        # Relative -> resolve against the live osgeo.org URL for this page
        # so we exercise real reachability. The site under verification is
        # presumed not yet deployed at its own domain.
        base = urljoin(BASE_URL + "/", page_hugo_url.lstrip("/"))
        return urljoin(base, raw_url)
    return raw_url


def check_one_url(url: str, session: requests.Session, timeout: float) -> tuple[bool, str]:
    """HEAD-check `url`. Falls back to GET if HEAD is rejected. Returns
    (ok, status_string)."""
    try:
        r = session.head(url, allow_redirects=True, timeout=timeout,
                         headers={"User-Agent": USER_AGENT})
        # Many servers either refuse HEAD outright (405/501) or lie about
        # the body; retry with GET in those cases.
        if r.status_code in (403, 405, 500, 501) or r.status_code >= 400:
            r = session.get(url, allow_redirects=True, timeout=timeout,
                            stream=True,
                            headers={"User-Agent": USER_AGENT})
            r.close()
        return r.status_code < 400, str(r.status_code)
    except requests.RequestException as e:
        return False, type(e).__name__


def check_urls_concurrent(
    urls: list[str],
    workers: int,
    timeout: float,
    verbose: bool,
) -> dict[str, tuple[bool, str]]:
    """HEAD-check every URL concurrently. Returns a dict url -> (ok, status)."""
    results: dict[str, tuple[bool, str]] = {}
    if not urls:
        return results
    session = requests.Session()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        future_map = {
            ex.submit(check_one_url, u, session, timeout): u for u in urls
        }
        done = 0
        total = len(future_map)
        for fut in concurrent.futures.as_completed(future_map):
            url = future_map[fut]
            try:
                results[url] = fut.result()
            except Exception as e:  # noqa: BLE001
                results[url] = (False, type(e).__name__)
            done += 1
            if verbose and (done % 25 == 0 or done == total):
                console.print(f"    [dim]link check {done}/{total}[/dim]")
    return results


def apply_fixes_in_file(path: Path, fixes: list[LinkFix]) -> tuple[int, dict[str, int]]:
    """Apply the link_fixes registry to every link target in `path`.

    Returns (total_substitutions, per_fix_counts). The file is rewritten
    in place; left alone if no changes are needed. Front matter is preserved
    verbatim so YAML-encoded URLs (aliases:, harvested_from:) are not touched
    -- the fixes only target body link targets.
    """
    if not fixes:
        return 0, {}
    text = path.read_text(encoding="utf-8")

    fm = ""
    body = text
    m = FRONT_MATTER_RE.match(text)
    if m:
        fm = m.group(0)
        body = text[m.end():]

    total = 0
    per_fix: dict[str, int] = {}

    def _try_fix(target: str) -> str:
        nonlocal total
        new_target, fix_id = apply_link_fix(target, fixes)
        if new_target != target:
            total += 1
            per_fix[fix_id] = per_fix.get(fix_id, 0) + 1
            return new_target
        return target

    def _rewrite_md_link(match: re.Match) -> str:
        target = match.group(1) or match.group(2)
        new = _try_fix(target)
        if new != target:
            return match.group(0).replace(target, new, 1)
        return match.group(0)

    def _rewrite_autolink(match: re.Match) -> str:
        target = match.group(1)
        new = _try_fix(target)
        return f"<{new}>" if new != target else match.group(0)

    def _rewrite_ref_def(match: re.Match) -> str:
        target = match.group(1)
        new = _try_fix(target)
        if new != target:
            return match.group(0).replace(target, new, 1)
        return match.group(0)

    body = MD_LINK_TARGET_RE.sub(_rewrite_md_link, body)
    body = MD_AUTOLINK_RE.sub(_rewrite_autolink, body)
    body = MD_REF_DEF_RE.sub(_rewrite_ref_def, body)

    if total:
        path.write_text(fm + body, encoding="utf-8")
    return total, per_fix


def remap_internal_links_in_file(path: Path) -> int:
    """Rewrite internal-absolute osgeo.org links in `path` to Hugo-relative.

    Returns the number of substitutions performed. The file is rewritten
    in place; left alone if no changes are needed.
    """
    text = path.read_text(encoding="utf-8")

    # Preserve front-matter verbatim -- only rewrite the body. We split on
    # the second `---` line.
    fm = ""
    body = text
    m = FRONT_MATTER_RE.match(text)
    if m:
        fm = m.group(0)
        body = text[m.end():]

    count = 0

    def _rewrite_md_link(match: re.Match) -> str:
        nonlocal count
        # MD_LINK_TARGET_RE has two alternatives -- group 1 is the angle-bracket
        # form, group 2 is the bare URL form. Exactly one will be set.
        target = match.group(1) or match.group(2)
        new_target = remap_internal_to_hugo(target)
        if new_target != target:
            count += 1
            return match.group(0).replace(target, new_target, 1)
        return match.group(0)

    def _rewrite_autolink(match: re.Match) -> str:
        nonlocal count
        target = match.group(1)
        new_target = remap_internal_to_hugo(target)
        if new_target != target:
            count += 1
            return f"<{new_target}>"
        return match.group(0)

    def _rewrite_ref_def(match: re.Match) -> str:
        nonlocal count
        target = match.group(1)
        new_target = remap_internal_to_hugo(target)
        if new_target != target:
            count += 1
            return match.group(0).replace(target, new_target, 1)
        return match.group(0)

    body = MD_LINK_TARGET_RE.sub(_rewrite_md_link, body)
    body = MD_AUTOLINK_RE.sub(_rewrite_autolink, body)
    body = MD_REF_DEF_RE.sub(_rewrite_ref_def, body)

    if count:
        path.write_text(fm + body, encoding="utf-8")
    return count


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify(
    exceptions: list[str],
    threshold: float,
    filter_re: re.Pattern | None,
    limit: int | None,
    verbose: bool,
    check_links: bool = True,
    link_workers: int = 16,
    link_timeout: float = 10.0,
    remap_internal: bool = False,
    write_fixes: bool = False,
    fixes: list[LinkFix] | None = None,
) -> tuple[list[CheckResult], list[LinkCheck], dict[str, int], dict[str, dict[str, int]]]:
    console.print(f"[bold]Fetching sitemap:[/bold] {PAGE_SITEMAP_URL}")
    sitemap_urls = fetch_sitemap_urls()
    console.print(f"  Sitemap pages: [bold]{len(sitemap_urls)}[/bold]")

    local_index = discover_local_pages()
    console.print(f"  Local harvested pages: [bold]{len(local_index)}[/bold]")
    console.print(f"  Exception list: [bold]{len(exceptions)}[/bold]")
    console.print()

    # Always derive remote_paths from the full sitemap so `--limit` (used
    # for smoke testing) does not falsely flag every unvisited local page
    # as missing-remote.
    remote_paths: set[str] = {
        normalise_path(urlparse(u).path) for u in sitemap_urls
    }
    results: list[CheckResult] = []
    # Accumulator: every link occurrence found in any local page.
    link_records: list[LinkCheck] = []
    # Map result.url -> index in `results` so we can patch in link totals.
    result_index_by_url: dict[str, int] = {}
    # Per-file remap counts (only populated when remap_internal=True).
    remap_summary: dict[str, int] = {}
    # Per-file link-fix counts, broken down by fix id (only when write_fixes=True).
    fix_summary: dict[str, dict[str, int]] = {}
    if fixes is None:
        fixes = []

    iterated = 0
    for url in sitemap_urls:
        url_path = normalise_path(urlparse(url).path)

        if filter_re and not filter_re.search(url_path):
            continue
        if limit is not None and iterated >= limit:
            break
        iterated += 1

        local_path = local_index.get(url_path)
        if local_path is None:
            for cand in url_to_candidate_paths(url_path):
                if cand.exists():
                    local_path = cand
                    break

        if is_excepted(url_path, exceptions):
            results.append(CheckResult(
                url=url_path,
                state="excepted",
                detail="in exception list",
                local_path=str(local_path.relative_to(SITE_ROOT)) if local_path else "",
                hugo_url=local_path_to_hugo_url(local_path) if local_path else "",
            ))
            if verbose:
                console.print(f"  [dim]skip (excepted):[/dim] {url_path}")
            continue

        if local_path is None:
            results.append(CheckResult(
                url=url_path,
                state="missing-local",
                detail="no local file found (no harvested_from match)",
            ))
            if verbose:
                console.print(f"  [red]missing-local:[/red] {url_path}")
            continue

        hugo_url = local_path_to_hugo_url(local_path)

        try:
            if verbose:
                console.print(f"  [cyan]checking:[/cyan] {url_path}")
            remote_text = fetch_remote_text(url)
        except requests.RequestException as e:
            results.append(CheckResult(
                url=url_path,
                state="error",
                detail=f"fetch failed: {e}"[:120],
                local_path=str(local_path.relative_to(SITE_ROOT)),
                hugo_url=hugo_url,
            ))
            time.sleep(REQUEST_DELAY)
            continue

        try:
            local_md = local_path.read_text(encoding="utf-8")
        except OSError as e:
            results.append(CheckResult(
                url=url_path,
                state="error",
                detail=f"read failed: {e}"[:120],
                local_path=str(local_path.relative_to(SITE_ROOT)),
                hugo_url=hugo_url,
            ))
            time.sleep(REQUEST_DELAY)
            continue

        # Optional in-place rewrite of internal-absolute URLs. Done before
        # we re-read for link extraction so the recorded links reflect the
        # final state of the file.
        if remap_internal:
            remapped = remap_internal_links_in_file(local_path)
            if remapped:
                remap_summary[str(local_path.relative_to(SITE_ROOT))] = remapped
                local_md = local_path.read_text(encoding="utf-8")
                if verbose:
                    console.print(
                        f"    [magenta]remapped {remapped} internal link(s)"
                        f"[/magenta] in {local_path.relative_to(SITE_ROOT)}"
                    )

        # Optional in-place rewrite using the link_fixes.json registry
        # (e.g. wiki MediaWiki path migration). Applied AFTER remap_internal
        # so absolute->relative rewrites win for in-tree URLs.
        if write_fixes and fixes:
            applied, per_fix = apply_fixes_in_file(local_path, fixes)
            if applied:
                fix_summary[str(local_path.relative_to(SITE_ROOT))] = per_fix
                local_md = local_path.read_text(encoding="utf-8")
                if verbose:
                    breakdown = ", ".join(f"{k}={v}" for k, v in per_fix.items())
                    console.print(
                        f"    [magenta]applied {applied} fix(es)[/magenta] "
                        f"in {local_path.relative_to(SITE_ROOT)} ({breakdown})"
                    )

        local_text = markdown_to_text(local_md)
        remote_words = to_word_stream(remote_text)
        local_words = to_word_stream(local_text)

        ratio, divergence = compare_word_streams(remote_words, local_words)
        if not remote_words and not local_words:
            state = "empty"
            detail = "no word content found on either side"
        elif ratio >= threshold:
            state = "match"
            detail = "word streams identical" if ratio == 1.0 \
                else f"within tolerance ({ratio:.1%})"
        else:
            state = "diff"
            detail = divergence

        # ----- Hyperlink scan -----
        page_links: list[LinkCheck] = []
        fixes_used_on_page = 0
        if check_links:
            for raw in extract_links_from_markdown(local_md):
                # Apply the registry so reachability reflects the post-fix
                # state, even if --write-fixes was not used.
                fixed, fix_id = apply_link_fix(raw, fixes) if fixes else (raw, "")
                effective = fixed
                kind = classify_link(effective)
                resolved = resolve_for_checking(effective, hugo_url) or ""
                remap_to = (
                    remap_internal_to_hugo(effective) if kind == "internal-absolute" else ""
                )
                if fix_id:
                    fixes_used_on_page += 1
                page_links.append(LinkCheck(
                    page_url=url_path,
                    raw_url=raw,
                    resolved=resolved,
                    kind=kind,
                    remap_to=remap_to,
                    fix_id=fix_id,
                ))
            link_records.extend(page_links)

        results.append(CheckResult(
            url=url_path,
            state=state,
            similarity=ratio,
            remote_words=len(remote_words),
            local_words=len(local_words),
            detail=detail,
            local_path=str(local_path.relative_to(SITE_ROOT)),
            hugo_url=hugo_url,
            link_total=len(page_links),
            link_remap_pending=sum(
                1 for lc in page_links if lc.kind == "internal-absolute"
            ),
            link_fixes_applied=fixes_used_on_page,
        ))
        result_index_by_url[url_path] = len(results) - 1

        time.sleep(REQUEST_DELAY)

    # Detect locally harvested pages whose upstream URL is no longer in the sitemap.
    for local_url, local_path in local_index.items():
        if filter_re and not filter_re.search(local_url):
            continue
        if local_url in remote_paths:
            continue
        if is_excepted(local_url, exceptions):
            continue
        results.append(CheckResult(
            url=local_url,
            state="missing-remote",
            detail="harvested_from URL no longer in upstream sitemap",
            local_path=str(local_path.relative_to(SITE_ROOT)),
            hugo_url=local_path_to_hugo_url(local_path),
        ))

    # ---- Run concurrent HTTP checks on every unique link target ----
    if check_links and link_records:
        unique_urls = sorted({
            lc.resolved for lc in link_records if lc.resolved
        })
        console.print(
            f"\n[bold]Checking [cyan]{len(unique_urls)}[/cyan] unique link "
            f"targets across [cyan]{len(link_records)}[/cyan] occurrences "
            f"({link_workers} workers)...[/bold]"
        )
        check_map = check_urls_concurrent(
            unique_urls, link_workers, link_timeout, verbose
        )
        # Apply check results to each occurrence + roll up per-page totals.
        broken_per_page: dict[str, int] = {}
        checked_per_page: dict[str, int] = {}
        for lc in link_records:
            if not lc.resolved:
                continue
            ok, status = check_map.get(lc.resolved, (None, ""))
            if ok is None:
                continue
            lc.ok = ok
            lc.status = status
            checked_per_page[lc.page_url] = checked_per_page.get(lc.page_url, 0) + 1
            if not ok:
                broken_per_page[lc.page_url] = broken_per_page.get(lc.page_url, 0) + 1
        for page_url, count in checked_per_page.items():
            idx = result_index_by_url.get(page_url)
            if idx is not None:
                results[idx].link_checked = count
        for page_url, count in broken_per_page.items():
            idx = result_index_by_url.get(page_url)
            if idx is not None:
                results[idx].link_broken = count
                # Surface broken links in the detail column so they pop out
                # of the main table without needing the secondary table.
                cur = results[idx]
                extra = f" [{count} broken link(s)]"
                if extra not in cur.detail:
                    cur.detail = (cur.detail + extra).strip()

    return results, link_records, remap_summary, fix_summary


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

STATE_COLORS = {
    "match": "green",
    "diff": "yellow",
    "empty": "yellow",
    "missing-local": "red",
    "missing-remote": "red",
    "excepted": "blue",
    "error": "magenta",
}
STATE_ORDER = {
    "diff": 0,
    "missing-local": 1,
    "missing-remote": 2,
    "error": 3,
    "empty": 4,
    "match": 5,
    "excepted": 6,
}


def render_table(results: list[CheckResult]) -> Table:
    table = Table(title="OSGeo Content Verification", show_lines=False)
    table.add_column("Endpoint", style="cyan", max_width=44, overflow="fold")
    table.add_column("State", style="bold")
    table.add_column("Sim.", justify="right")
    table.add_column("Words", justify="right")
    table.add_column("Links\n(brk/chk/tot)", justify="right")
    table.add_column("Remap?", justify="right")
    table.add_column("Detail", style="dim", max_width=46, overflow="fold")

    for r in sorted(results, key=lambda r: (STATE_ORDER.get(r.state, 99), r.url)):
        color = STATE_COLORS.get(r.state, "white")
        sim = f"{r.similarity:.1%}" if r.similarity is not None else "-"
        words = f"{r.remote_words}/{r.local_words}" if (r.remote_words or r.local_words) else "-"
        if r.link_total:
            link_cell = f"{r.link_broken}/{r.link_checked}/{r.link_total}"
            if r.link_broken:
                link_cell = f"[red]{link_cell}[/red]"
        else:
            link_cell = "-"
        remap_cell = str(r.link_remap_pending) if r.link_remap_pending else "-"
        if r.link_remap_pending:
            remap_cell = f"[yellow]{remap_cell}[/yellow]"
        table.add_row(
            r.url,
            f"[{color}]{r.state}[/{color}]",
            sim,
            words,
            link_cell,
            remap_cell,
            r.detail,
        )
    return table


def render_broken_links_table(link_records: list[LinkCheck]) -> Table | None:
    broken = [lc for lc in link_records if lc.ok is False]
    if not broken:
        return None
    table = Table(title="Broken Hyperlinks", show_lines=False)
    table.add_column("On page", style="cyan", max_width=36, overflow="fold")
    table.add_column("Link", style="white", max_width=48, overflow="fold")
    table.add_column("Kind", style="bold")
    table.add_column("Status", style="red")
    for lc in sorted(broken, key=lambda l: (l.page_url, l.resolved)):
        shown = lc.raw_url if len(lc.raw_url) < 48 else lc.resolved
        table.add_row(lc.page_url, shown, lc.kind, lc.status)
    return table


def render_markdown(
    results: list[CheckResult],
    link_records: list[LinkCheck] | None = None,
    remap_summary: dict[str, int] | None = None,
    fix_summary: dict[str, dict[str, int]] | None = None,
) -> str:
    lines = [
        "# OSGeo Content Verification",
        "",
        "| Endpoint | State | Sim. | Words (R/L) | Links broken/checked/total | Remap pending | Detail |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in sorted(results, key=lambda r: (STATE_ORDER.get(r.state, 99), r.url)):
        sim = f"{r.similarity:.1%}" if r.similarity is not None else "-"
        words = f"{r.remote_words}/{r.local_words}" if (r.remote_words or r.local_words) else "-"
        link_cell = (
            f"{r.link_broken}/{r.link_checked}/{r.link_total}"
            if r.link_total else "-"
        )
        remap_cell = str(r.link_remap_pending) if r.link_remap_pending else "-"
        detail = r.detail.replace("|", "\\|")
        lines.append(
            f"| `{r.url}` | {r.state} | {sim} | {words} | {link_cell} | "
            f"{remap_cell} | {detail} |"
        )

    if link_records is not None:
        broken = [lc for lc in link_records if lc.ok is False]
        lines.append("")
        lines.append("## Broken Hyperlinks")
        lines.append("")
        if not broken:
            lines.append("_No broken hyperlinks found._")
        else:
            lines.append("| Page | Link | Kind | Status |")
            lines.append("| --- | --- | --- | --- |")
            for lc in sorted(broken, key=lambda l: (l.page_url, l.resolved)):
                shown = lc.raw_url.replace("|", "\\|")
                lines.append(
                    f"| `{lc.page_url}` | `{shown}` | {lc.kind} | {lc.status} |"
                )

    if remap_summary:
        lines.append("")
        lines.append("## Internal Link Remap Summary")
        lines.append("")
        lines.append("| File | Substitutions |")
        lines.append("| --- | ---: |")
        for f, n in sorted(remap_summary.items()):
            lines.append(f"| `{f}` | {n} |")

    if fix_summary:
        lines.append("")
        lines.append("## Link-Fix Registry Substitutions")
        lines.append("")
        lines.append("| File | Fix ID | Count |")
        lines.append("| --- | --- | ---: |")
        for f, per_fix in sorted(fix_summary.items()):
            for fix_id, count in sorted(per_fix.items()):
                lines.append(f"| `{f}` | `{fix_id}` | {count} |")

    return "\n".join(lines) + "\n"


def render_nginx_config(results: list[CheckResult]) -> str:
    """Build an nginx redirect map from legacy WordPress URLs to Hugo URLs.

    Strategy:
      * For every endpoint where we have a local Hugo equivalent, emit a
        `location = /old-path { return 301 /new-path/; }` block.
      * When old-path == new-path, emit the line as a comment so the file
        documents the full mapping but nginx does not create a no-op redirect.
      * For `missing-local` (upstream URL with no local equivalent), emit a
        `return 410 Gone;` block so legacy URLs do not 404 silently.
      * `error` results are skipped (we cannot reason about them).

    The output is meant to be included inside a server { } block:
        include /etc/nginx/snippets/osgeo-redirects.conf;
    """
    lines = [
        "# Auto-generated by scripts/verify_content.py -- do not edit by hand.",
        "#",
        "# Legacy osgeo.org (WordPress) URL -> Hugo URL redirects.",
        "# Include from a server { } block:",
        "#   include /etc/nginx/snippets/osgeo-redirects.conf;",
        "#",
        "# Categories:",
        "#   ACTIVE   -- old URL differs from Hugo URL, emits a 301",
        "#   NOOP     -- old URL == Hugo URL (kept as comment for documentation)",
        "#   GONE     -- upstream page has no local equivalent (returns 410)",
        "#",
    ]
    active: list[tuple[str, str, str]] = []  # (old, new, state)
    noop: list[tuple[str, str]] = []         # (old, state)
    gone: list[str] = []

    for r in sorted(results, key=lambda r: r.url):
        if r.state == "error":
            continue
        if r.state == "missing-local":
            gone.append(r.url)
            continue
        if not r.hugo_url:
            continue
        old = r.url
        new = r.hugo_url
        if normalise_path(old) == normalise_path(new):
            noop.append((old, r.state))
        else:
            active.append((old, new, r.state))

    lines.append(f"# ACTIVE redirects: {len(active)}")
    lines.append(f"# NOOP entries:     {len(noop)}")
    lines.append(f"# GONE entries:     {len(gone)}")
    lines.append("")

    if active:
        lines.append("# --- 301 redirects (legacy URL -> Hugo URL) ---")
        for old, new, state in active:
            lines.append(f"# [{state}]")
            lines.append(f"location = {old} {{ return 301 {new}; }}")
            # Also handle the slash-less variant since nginx is exact-match.
            if old.endswith("/") and old != "/":
                lines.append(f"location = {old.rstrip('/')} {{ return 301 {new}; }}")
        lines.append("")

    if noop:
        lines.append("# --- No-op (old == new, listed for completeness) ---")
        for old, state in noop:
            lines.append(f"# [{state}] location = {old} -> {old}")
        lines.append("")

    if gone:
        lines.append("# --- Upstream pages with no local equivalent (410 Gone) ---")
        for old in gone:
            lines.append(f"location = {old} {{ return 410; }}")
            if old.endswith("/") and old != "/":
                lines.append(f"location = {old.rstrip('/')} {{ return 410; }}")
        lines.append("")

    return "\n".join(lines) + "\n"


def summarise(results: list[CheckResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in results:
        counts[r.state] = counts.get(r.state, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Hugo content against upstream osgeo.org"
    )
    parser.add_argument("--output", choices=["table", "markdown", "json"],
                        default="table", help="Output format (default: table)")
    parser.add_argument("--exceptions", type=Path, default=EXCEPTION_LIST_FILE,
                        help="Path to JSON exception list (default: scripts/verify_exceptions.json)")
    parser.add_argument("--threshold", type=float, default=1.0,
                        help="Similarity ratio at/above which a page is considered a match "
                             "(default: 1.0 = strict word-for-word).")
    parser.add_argument("--filter", type=str, default=None,
                        help="Only check URL paths matching this regex")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most N sitemap URLs (useful for smoke tests)")
    parser.add_argument("--save", type=Path, default=None,
                        help="Write the rendered report to this file as well")
    parser.add_argument("--nginx-config", type=Path, default=None,
                        help="Write an nginx redirect snippet to this path "
                             "(legacy WordPress URLs -> Hugo URLs)")
    parser.add_argument("--skip-links", action="store_true",
                        help="Skip the hyperlink walk + HTTP reachability check")
    parser.add_argument("--remap-internal", action="store_true",
                        help="Rewrite https://www.osgeo.org/* links in local "
                             "markdown to Hugo-relative paths (modifies files)")
    parser.add_argument("--write-fixes", action="store_true",
                        help="Rewrite link targets in local markdown using "
                             "scripts/link_fixes.json (modifies files). The "
                             "fixes are also applied at check-time regardless "
                             "of this flag, so reachability reflects post-fix "
                             "URLs.")
    parser.add_argument("--fixes-file", type=Path, default=LINK_FIXES_FILE,
                        help="Path to the link-fixes registry "
                             "(default: scripts/link_fixes.json)")
    parser.add_argument("--link-workers", type=int, default=16,
                        help="Concurrent HTTP workers for link check (default: 16)")
    parser.add_argument("--link-timeout", type=float, default=10.0,
                        help="Per-link HTTP timeout in seconds (default: 10)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show per-page progress")
    args = parser.parse_args()

    exceptions = load_exception_list(args.exceptions)
    fixes = load_link_fixes(args.fixes_file)
    filter_re = re.compile(args.filter) if args.filter else None

    console.print("[bold green]OSGeo Content Verifier[/bold green]")
    console.print(f"  Content dir: {CONTENT_DIR}")
    console.print(f"  Exceptions:  {args.exceptions}")
    console.print(f"  Threshold:   {args.threshold:.0%}")
    console.print(f"  Link check:  {'off' if args.skip_links else 'on'}")
    console.print(f"  Link fixes:  {len(fixes)} registered ({args.fixes_file.name})")
    if args.remap_internal:
        console.print("  Remap:       [magenta]rewrite internal osgeo.org links[/magenta]")
    if args.write_fixes:
        console.print("  Fixes:       [magenta]write registry fixes to disk[/magenta]")
    if filter_re:
        console.print(f"  Filter:      {args.filter}")
    if args.limit:
        console.print(f"  Limit:       {args.limit}")
    console.print()

    results, link_records, remap_summary, fix_summary = verify(
        exceptions=exceptions,
        threshold=args.threshold,
        filter_re=filter_re,
        limit=args.limit,
        verbose=args.verbose,
        check_links=not args.skip_links,
        link_workers=args.link_workers,
        link_timeout=args.link_timeout,
        remap_internal=args.remap_internal,
        write_fixes=args.write_fixes,
        fixes=fixes,
    )

    if args.output == "json":
        payload = json.dumps(
            {
                "summary": summarise(results),
                "results": [r.to_dict() for r in results],
                "links": [lc.to_dict() for lc in link_records],
                "remap_summary": remap_summary,
                "fix_summary": fix_summary,
            },
            indent=2,
        )
        console.print(payload)
        if args.save:
            args.save.write_text(payload, encoding="utf-8")
    elif args.output == "markdown":
        md = render_markdown(results, link_records, remap_summary, fix_summary)
        summary = summarise(results)
        md += "\n## Summary\n\n"
        for state in sorted(summary):
            md += f"- **{state}**: {summary[state]}\n"
        md += f"- **total pages**: {len(results)}\n"
        broken_links = sum(1 for lc in link_records if lc.ok is False)
        checked_links = sum(1 for lc in link_records if lc.ok is not None)
        md += f"- **links checked**: {checked_links}\n"
        md += f"- **links broken**: {broken_links}\n"
        if remap_summary:
            md += f"- **files remapped**: {len(remap_summary)} "
            md += f"({sum(remap_summary.values())} substitutions)\n"
        if fix_summary:
            total_fixes = sum(sum(v.values()) for v in fix_summary.values())
            md += f"- **registry fixes applied**: {total_fixes} "
            md += f"in {len(fix_summary)} file(s)\n"
        console.print(md)
        if args.save:
            args.save.write_text(md, encoding="utf-8")
    else:
        table = render_table(results)
        console.print(table)
        broken_tbl = render_broken_links_table(link_records)
        if broken_tbl is not None:
            console.print()
            console.print(broken_tbl)
        console.print()
        console.print("[bold]Summary:[/bold]")
        for state, count in sorted(summarise(results).items()):
            color = STATE_COLORS.get(state, "white")
            console.print(f"  [{color}]{state}[/{color}]: {count}")
        console.print(f"  [bold]total pages: {len(results)}[/bold]")
        broken_links = sum(1 for lc in link_records if lc.ok is False)
        checked_links = sum(1 for lc in link_records if lc.ok is not None)
        if checked_links:
            color = "red" if broken_links else "green"
            console.print(
                f"  [{color}]links broken: {broken_links}/{checked_links} checked[/{color}]"
            )
        if remap_summary:
            console.print(
                f"  [magenta]remapped: {sum(remap_summary.values())} link(s) "
                f"in {len(remap_summary)} file(s)[/magenta]"
            )
        if fix_summary:
            total_fixes = sum(sum(v.values()) for v in fix_summary.values())
            console.print(
                f"  [magenta]registry fixes applied: {total_fixes} in "
                f"{len(fix_summary)} file(s)[/magenta]"
            )
        if args.save:
            args.save.write_text(
                render_markdown(results, link_records, remap_summary, fix_summary),
                encoding="utf-8",
            )
            console.print(f"\n[dim]Saved markdown report to {args.save}[/dim]")

    if args.nginx_config:
        nginx_cfg = render_nginx_config(results)
        args.nginx_config.write_text(nginx_cfg, encoding="utf-8")
        console.print(f"\n[dim]Wrote nginx redirect snippet to {args.nginx_config}[/dim]")

    # Exit non-zero if any non-clean state is present (useful for CI).
    bad_states = {"diff", "missing-local", "missing-remote", "error"}
    bad = sum(1 for r in results if r.state in bad_states)
    bad += sum(1 for r in results if r.link_broken > 0)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
