"""Render-aware fetch layer for runtime V2.3 (site-direct-only).

V2.3 removes external search dependencies but keeps the bounded render
fallback required by SPA-hosted municipal sites. The provider contract
stays (status_code, body): render.py wraps an existing fetch_fn and
converts SPA-shell responses (200, "") into rendered DOM through bounded
headless Chrome. Fail closed: render failure stays an empty shell, never
fabricated content. Render security reuses runtime.discovery.security
validate_url; no credentials, no external search hosts.
"""

import hashlib
import os
import shutil
import subprocess
import tempfile

from runtime.discovery.providers import FetchResult, HttpFetchProvider, ReplayFetchProvider
from runtime.discovery.security import InvalidUrlError, validate_url
from runtime.discovery_v2.sitemap_fetch import MAX_SIZE

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
]
RENDER_TIMEOUT_S = 45
VIRTUAL_TIME_BUDGET_MS = 12000


def _chrome_binary():
    for candidate in CHROME_CANDIDATES:
        if candidate.startswith("/"):
            if os.path.exists(candidate):
                return candidate
        else:
            path = shutil.which(candidate)
            if path:
                return path
    return None


def render_url(url, timeout=RENDER_TIMEOUT_S):
    """Render one URL with bounded headless Chrome.

    Returns (status_code, body) with the same semantics as
    sitemap_fetch.bounded_fetch: (0, "") on any failure. The URL must pass
    validate_url (SSRF/private/scheme rules) before Chrome is launched.
    """
    validate_url(url)
    binary = _chrome_binary()
    if binary is None:
        return (0, "")
    with tempfile.TemporaryDirectory(prefix="v23render-") as user_data_dir:
        try:
            proc = subprocess.Popen(
                [binary, "--headless=new", "--disable-gpu", "--no-first-run",
                 "--user-data-dir=" + user_data_dir,
                 "--virtual-time-budget=%d" % VIRTUAL_TIME_BUDGET_MS,
                 "--timeout=%d" % int(timeout * 1000),
                 "--dump-dom", url],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                # Own process group so a hung renderer can be killed
                # reliably on timeout (macOS does not kill grandchildren
                # on its own).
                start_new_session=True,
            )
        except OSError:
            return (0, "")
        try:
            # Chrome enforces its own --timeout; allow a small grace so
            # its DOM dump lands before we kill the process group.
            stdout, _stderr = proc.communicate(timeout=timeout + 5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
            proc.communicate()
            return (0, "")
    dom = stdout or ""
    if not dom.strip():
        return (0, "")
    if len(dom) > MAX_SIZE:
        dom = dom[:MAX_SIZE]
    return (200, dom)


class RenderFetchFn:
    """Wrap a (status_code, body) fetch_fn; render once on SPA shells.

    audit (optional list) receives ("http", url) / ("render", url) tuples
    for the V2.3 network-call audit. max_renders bounds renders per
    provider instance (per-municipality budget); None means unbounded
    apart from SiteDirectProvider's own URL budget.
    """

    def __init__(self, inner_fetch_fn, render_fn=render_url,
                 max_renders=None, audit=None):
        self.inner = inner_fetch_fn
        self.render_fn = render_fn
        self.max_renders = max_renders
        self.audit = audit if audit is not None else []
        self.render_count = 0
        self.rendered_urls = []

    def __call__(self, url):
        self.audit.append(("http", url))
        status_code, body = self.inner(url)
        if status_code != 200 or body != "":
            return (status_code, body)
        # SPA shell per the frozen bounded_fetch contract: (200, "").
        try:
            validate_url(url)
        except InvalidUrlError:
            return (200, "")
        if self.max_renders is not None and self.render_count >= self.max_renders:
            return (200, "")
        self.render_count += 1
        self.audit.append(("render", url))
        rendered_status, rendered_body = self.render_fn(url)
        if rendered_status == 200 and rendered_body:
            if len(rendered_body) > MAX_SIZE:
                rendered_body = rendered_body[:MAX_SIZE]
            self.rendered_urls.append(url)
            return (200, rendered_body)
        return (200, "")


class RenderAwareFetchProvider(HttpFetchProvider):
    """HttpFetchProvider with the bounded render fallback (V2.3).

    A render_required outcome (SPA shell) is converted to a successful
    rendered fetch once; render failure keeps the frozen render_required
    path, which the orchestrator treats as a fetch error (fail closed).
    """

    def __init__(self, render_fn=render_url, **kwargs):
        super().__init__(**kwargs)
        self.render_fn = render_fn
        self.render_count = 0
        self.rendered_urls = []

    def fetch(self, url):
        fr = super().fetch(url)
        if fr.status != "render_required":
            return fr
        try:
            validate_url(url)
        except InvalidUrlError:
            return fr
        status, dom = self.render_fn(url)
        if status != 200 or not dom:
            return fr
        if len(dom) > MAX_SIZE:
            dom = dom[:MAX_SIZE]
        self.render_count += 1
        self.rendered_urls.append(url)
        return FetchResult(
            url=url, status="success", content=dom,
            content_hash=hashlib.sha256(dom.encode("utf-8")).hexdigest(),
            fetch_method="rendered_browser", retrieved_at=None,
            final_url=fr.final_url or url,
        )


class RenderReplayFetchProvider(ReplayFetchProvider):
    """Replay fetch with an explicit render-manifest for SPA pages.

    Pages missing from the base manifest fail exactly like the frozen
    ReplayFetchProvider; pages present in render_manifest succeed as
    rendered_browser fetches. Used by replay tests and official replay
    regression so SPA coverage is explicit, never a silent bypass.
    """

    def __init__(self, manifest, render_manifest=None):
        super().__init__(manifest)
        self.render_manifest = render_manifest or {}
        self.render_count = 0
        self.rendered_urls = []

    def fetch(self, url):
        fr = super().fetch(url)
        if fr.status == "failed" and url in self.render_manifest:
            dom = self.render_manifest[url]
            self.render_count += 1
            self.rendered_urls.append(url)
            return FetchResult(
                url=url, status="success", content=dom,
                content_hash=hashlib.sha256(dom.encode("utf-8")).hexdigest(),
                fetch_method="rendered_browser",
                retrieved_at="FIXTURE_TIME", final_url=url,
            )
        return fr
