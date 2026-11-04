#!/usr/bin/env python3
"""Build the Discount Bond Database static site."""
import os, html, json

# ---------------------------------------------------------------- launch switches
# Flip both of these when the site goes live, then re-run: python3 build.py
NOINDEX = True          # True while the site is a test build - keeps it out of Google.
GA_MEASUREMENT_ID = ""  # e.g. "G-XXXXXXXXXX". Empty = no analytics emitted.

# ---------------------------------------------------------------- site settings
NOINDEX = False
GA_MEASUREMENT_ID = "G-JNSBW1CKXE"
CONTACT_EMAIL = "mpelger@stanford.edu"
SITE_UPDATED  = "November 2026"
# ---------------------------------------------------------------------------------

NAV = [("index.html","Home"),("united-states.html","United States"),("germany.html","Germany"),
       ("japan.html","Japan"),("united-kingdom.html","United Kingdom"),("canada.html","Canada"),
       ("switzerland.html","Switzerland"),("methodology.html","Data & Code"),("faq.html","FAQ")]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700'
         '&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">')

# Hash-target behaviour: a link to an anchor inside a closed <details> opens it before scrolling.
# Kept out of shell()'s f-string because the braces would be read as placeholders.
# Citation store: the single source for the "Papers and how to cite" blocks and for the
# inline Cite control on every dataset section. "doi" is absent for the working paper.
PAPERS = json.loads(r'''{"paper-kr": {"text": "Filipovic, D., M. Pelger, and Y. Ye (2026). Stripping the Discount Curve — A Robust Machine Learning Approach. Management Science 72(9), 8057–8120. https://doi.org/10.1287/mnsc.2023.01401", "bibtex": "@article{FilipovicPelgerYe2026Stripping,\n  author  = {Filipovic, Damir and Pelger, Markus and Ye, Ye},\n  title   = {Stripping the Discount Curve---{A} Robust Machine Learning Approach},\n  journal = {Management Science},\n  year    = {2026},\n  volume  = {72},\n  number  = {9},\n  pages   = {8057--8120},\n  doi     = {10.1287/mnsc.2023.01401}\n}", "doi": "10.1287/mnsc.2023.01401", "ssrn": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4058150"}, "paper-factors": {"text": "Filipovic, D., M. Pelger, and Y. Ye (2026). Shrinking the Term Structure. Review of Finance, advance article. https://doi.org/10.1093/rof/rfag033", "bibtex": "@article{FilipovicPelgerYe2026Shrinking,\n  author  = {Filipovic, Damir and Pelger, Markus and Ye, Ye},\n  title   = {Shrinking the Term Structure},\n  journal = {Review of Finance},\n  year    = {2026},\n  note    = {Advance article},\n  doi     = {10.1093/rof/rfag033}\n}", "doi": "10.1093/rof/rfag033", "ssrn": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4182649"}, "paper-krt": {"text": "Filipovic, D., M. Pelger, and R. Wang (2026). Stripping Discount Curves Across Currencies: Transfer Learning from US Treasuries. Working paper. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7092381", "bibtex": "@unpublished{FilipovicPelgerWang2026Transfer,\n  author  = {Filipovic, Damir and Pelger, Markus and Wang, Rose},\n  title   = {Stripping Discount Curves Across Currencies: Transfer Learning from {US} Treasuries},\n  year    = {2026},\n  note    = {Working paper},\n  url     = {https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7092381}\n}", "ssrn": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7092381"}}''')
CITE_JSON = json.dumps(PAPERS, ensure_ascii=False)

# Inline "Cite" control. Sits at the end of a dataset description, in the text flow, so it
# wraps as one unit when the line is full. The popover itself is built by script from
# window.__CITES, so there is one citation store, not two.
QUOTE_SVG = ('<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
             '<path d="M6.9 3.1 7.9 4.8C6.6 5.4 5.6 6.4 5.3 7.6c.26-.06.53-.1.8-.1 1.3 0 2.3 1 2.3 2.4 '
             '0 1.4-1.1 2.5-2.6 2.5-1.7 0-3-1.5-3-3.8 0-2.5 1.6-4.6 4.1-5.5zm7 0 1 1.7c-1.3.6-2.3 1.6-2.6 '
             '2.8.26-.06.53-.1.8-.1 1.3 0 2.3 1 2.3 2.4 0 1.4-1.1 2.5-2.6 2.5-1.7 0-3-1.5-3-3.8 '
             '0-2.5 1.6-4.6 4.1-5.5z"/></svg>')

def cite(key, what):
    """key -> an entry in PAPERS; what -> dataset name, for the accessible label."""
    return (' <button type="button" class="cite-btn" data-cite="' + key + '"'
            ' aria-expanded="false" aria-haspopup="dialog"'
            ' aria-label="Cite ' + what + '">' + QUOTE_SVG + '<span>Cite</span></button>')

REVEAL_JS = """<script>
window.__CITES = __CITE_JSON__;
(function () {
  var userMoved = false;
  ['wheel', 'touchstart', 'keydown'].forEach(function (t) {
    window.addEventListener(t, function () { userMoved = true; }, { passive: true, once: true });
  });
  function reveal() {
    if (location.hash.length < 2) return;
    var el;
    try { el = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (e) { return; }
    if (!el) return;
    var d = el.closest('details');
    while (d) { d.open = true; d = d.parentElement ? d.parentElement.closest('details') : null; }
    el.scrollIntoView();
  }
  window.addEventListener('hashchange', function () { userMoved = false; reveal(); });
  /* Copy citation / BibTeX */
  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('button.copy') : null;
    if (!b) return;
    var rec = (window.__CITES || {})[b.dataset.cite];
    var text = rec ? rec[b.dataset.kind] : '';
    if (!text) return;
    var done = function () {
      if (b.dataset.quiet === '1') {           /* icon button: keep the icon, flag it instead */
        b.classList.add('ok');
        setTimeout(function () { b.classList.remove('ok'); }, 1500);
        return;
      }
      var was = b.textContent;
      b.textContent = 'Copied';
      b.classList.add('ok');
      setTimeout(function () { b.textContent = was; b.classList.remove('ok'); }, 1500);
    };
    var fallback = function () {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', '');
      ta.style.position = 'absolute'; ta.style.left = '-9999px';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (err) {}
      document.body.removeChild(ta);
      if (ok) done();
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
  });
  /* ---- inline dataset citation: one popover, reused by every Cite button ---- */
  (function () {
    var pop, backdrop, trigger = null, kinds = [], active = 0;
    var LABEL = { bibtex: 'BibTeX', doi: 'DOI', ssrn: 'SSRN' };
    var COPY_SVG = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
      '<rect x="5.6" y="5.6" width="8.2" height="8.8" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/>' +
      '<path d="M10.6 3.6H3.7a1.5 1.5 0 0 0-1.5 1.5v6.9" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>';
    var EXT_SVG = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
      '<path d="M6.5 3.5h-3v9h9v-3M9.5 3.5h3v3M12.5 3.5 7 9"/></svg>';
    function esc(t) {
      return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                      .replace(/"/g, '&quot;');
    }
    function isSheet() { return window.matchMedia('(max-width:620px)').matches; }
    function rec() { return (window.__CITES || {})[trigger.dataset.cite] || {}; }

    function build() {
      if (pop) return;
      backdrop = document.createElement('div');
      backdrop.className = 'citebd';
      backdrop.hidden = true;
      backdrop.addEventListener('click', close);
      document.body.appendChild(backdrop);

      pop = document.createElement('div');
      pop.className = 'citepop';
      pop.hidden = true;
      pop.setAttribute('role', 'dialog');
      pop.setAttribute('aria-label', 'Cite this dataset');
      pop.innerHTML = '<div class="cp-in">' +
        '<div class="cp-head"><span>Cite this dataset</span>' +
        '<button type="button" class="cp-x" aria-label="Close">×</button></div>' +
        '<div class="cp-tabs" role="tablist" aria-label="Citation format"></div>' +
        '<div class="cp-body"></div></div>';
      document.body.appendChild(pop);
      pop.querySelector('.cp-x').addEventListener('click', close);
      pop.querySelector('.cp-tabs').addEventListener('click', function (e) {
        var b = e.target.closest('button'); if (b) select(+b.dataset.i);
      });
      pop.querySelector('.cp-tabs').addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        select((active + d + kinds.length) % kinds.length, true);
      });
    }

    function panel(kind) {
      var r = rec(), key = esc(trigger.dataset.cite);
      var btn = function (k, what) {
        return '<button type="button" class="copy ic" data-cite="' + key + '" data-kind="' + k +
               '" data-quiet="1" aria-label="Copy ' + what + '">' + COPY_SVG + '</button>';
      };
      if (kind === 'bibtex') {
        return '<div class="cp-wrap"><pre class="cp-pre">' + esc(r.bibtex) + '</pre>' +
               btn('bibtex', 'BibTeX entry') + '</div>';
      }
      var url = kind === 'doi' ? 'https://doi.org/' + r.doi : r.ssrn;
      return '<div class="cp-lab">' + LABEL[kind] + '</div>' +
             '<div class="cp-wrap"><div class="cp-val">' + esc(r[kind]) + '</div>' +
             btn(kind, LABEL[kind]) + '</div>' +
             '<a class="cp-link" href="' + esc(url) + '" target="_blank" rel="noopener">' +
             esc(url) + EXT_SVG + '</a>';
    }

    function select(i, focus) {
      active = i;
      var tabs = pop.querySelectorAll('.cp-tabs button');
      for (var n = 0; n < tabs.length; n++) {
        tabs[n].setAttribute('aria-selected', n === i ? 'true' : 'false');
        tabs[n].tabIndex = n === i ? 0 : -1;
      }
      var body = pop.querySelector('.cp-body');
      body.innerHTML = '<div class="cp-panel" role="tabpanel" tabindex="0" aria-labelledby="' +
                       tabs[i].id + '">' + panel(kinds[i]) + '</div>';
      if (focus) tabs[i].focus();
    }

    function place() {
      if (isSheet()) {
        pop.classList.add('sheet');
        pop.style.left = pop.style.top = '';
        backdrop.hidden = false;
        return;
      }
      pop.classList.remove('sheet');
      backdrop.hidden = true;
      var r = trigger.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
      var docW = document.documentElement.clientWidth;
      var left = Math.min(Math.max(12, r.left), docW - w - 12) + window.pageXOffset;
      var top = (r.bottom + 8 + h > window.innerHeight && r.top - 8 - h > 0)
        ? r.top - h - 8 : r.bottom + 8;
      pop.style.left = left + 'px';
      pop.style.top = (top + window.pageYOffset) + 'px';
    }

    function open(btn) {
      build();
      if (trigger === btn && !pop.hidden) { close(); return; }
      trigger = btn;
      var r = rec();
      kinds = ['bibtex', 'doi', 'ssrn'].filter(function (k) { return r[k]; });
      var tabs = pop.querySelector('.cp-tabs'), html = '';
      for (var i = 0; i < kinds.length; i++) {
        html += '<button type="button" role="tab" id="cp-tab-' + kinds[i] + '" data-i="' + i +
                '" aria-selected="false" tabindex="-1">' + LABEL[kinds[i]] + '</button>';
      }
      tabs.innerHTML = html;
      pop.hidden = false;
      select(0);
      place();
      btn.setAttribute('aria-expanded', 'true');
      pop.querySelector('.cp-tabs button').focus();
    }

    function close() {
      if (!pop || pop.hidden) return;
      pop.hidden = true;
      backdrop.hidden = true;
      if (trigger) {
        trigger.setAttribute('aria-expanded', 'false');
        if (pop.contains(document.activeElement) || document.activeElement === document.body) {
          trigger.focus();
        }
      }
      trigger = null;
    }

    document.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('.cite-btn') : null;
      if (b) { e.preventDefault(); open(b); return; }
      if (pop && !pop.hidden && !pop.contains(e.target)) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
    });
    window.addEventListener('resize', function () { if (pop && !pop.hidden) place(); });
  })();
  /* status tooltips: hover and keyboard focus are pure CSS; a tap toggles, and a tap elsewhere
     or Escape closes. */
  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('.stat') : null;
    var open = document.querySelectorAll('.stat.on');
    for (var i = 0; i < open.length; i++) { if (open[i] !== t) open[i].classList.remove('on'); }
    if (t) { t.classList.toggle('on'); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelectorAll('.stat.on');
    for (var i = 0; i < open.length; i++) { open[i].classList.remove('on'); }
  });
  reveal();
  /* fonts and images can shift the page after the first pass, so land it again unless the
     reader has already started scrolling */
  window.addEventListener('load', function () { if (!userMoved) reveal(); });
})();
</script>"""

def shell(current, title, body):
    updated = f"<span>Last updated: {SITE_UPDATED}</span>" if SITE_UPDATED else ""
    contact = f' · Contact: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>' if CONTACT_EMAIL else ""
    robots = ('<meta name="robots" content="noindex, nofollow">\n' if NOINDEX else '')
    analytics = (f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>""" if GA_MEASUREMENT_ID else
"<!-- Google Analytics: set GA_MEASUREMENT_ID in build.py at go-live. -->")
    nav = "\n".join(
        '      <li><a href="{h}"{c}>{t}</a></li>'.format(
            h=h, t=html.escape(t), c=' aria-current="page"' if h == current else '')
        for h, t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="Government zero-coupon yield curve estimates for six major government bond markets.">
{robots}<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="assets/style.css">
{analytics}
</head>
<body>
<header class="masthead">
  <div class="wrap">
    <a class="brand" href="index.html">Discount Bond Database</a>
    <div class="tagline">Government zero-coupon yield curves for six major government bond markets</div>
  </div>
  <nav class="main" aria-label="Main">
    <div class="wrap">
      <ul>
{nav}
      </ul>
    </div>
  </nav>
</header>

<main>
  <div class="wrap">
{body}
  </div>
</main>

<footer class="site">
  <div class="wrap inner">
    <span>Discount Bond Database</span>
    <span><a href="methodology.html">Data &amp; Code</a> · <a href="faq.html">FAQ</a> · <a href="methodology.html#cite">How to cite</a>{contact}</span>
    {updated}
  </div>
</footer>
{REVEAL_JS.replace("__CITE_JSON__", CITE_JSON)}
</body>
</html>
"""

# --------------------------------------------------------------------------- data
COUNTRIES = {
 "germany":        dict(name="Germany",        adj="German",
                        kr=("July 1, 1987",      "9,091"), krt=("December 14, 1998", "6,007"),
                        max_day="11,856", max_year="32.5", max_month="389"),
 "japan":          dict(name="Japan",          adj="Japanese",
                        kr=("March 22, 1988",    "8,575"), krt=("January 4, 1989",   "8,071"),
                        max_day="14,731", max_year="40.4", max_month="484"),
 "united-kingdom": dict(name="United Kingdom", adj="U.K.",
                        kr=("July 1, 1987",      "9,018"), krt=("July 1, 1987",      "8,739"),
                        max_day="20,115", max_year="55.1", max_month="661"),
 "canada":         dict(name="Canada",         adj="Canadian",
                        kr=("July 2, 1987",      "8,944"), krt=("December 29, 1988", "8,381"),
                        max_day="18,477", max_year="50.6", max_month="607"),
 "switzerland":    dict(name="Switzerland",    adj="Swiss",
                        kr=("February 16, 1994", "7,302"), krt=("February 16, 1994", "7,064"),
                        max_day="18,263", max_year="50.0", max_month="600"),
}
END = "March 31, 2023"
VARIANTS = ["Daily observations, daily maturities","Daily observations, monthly maturities",
            "Monthly observations, daily maturities","Monthly observations, monthly maturities"]

def drive(file_id):
    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

# International files on the shared Drive, uploaded 2026-11-01. CSV for all four variants;
# Parquet only for the daily-observations / daily-maturities file, the one large enough for
# the format to be worth it. File name -> Drive id:

DRIVE_IDS = {
    "canada_kr_yield_panel_daily_frequency_daily_maturity.csv":
        "1piEktA5gcH7MlAhn1SkI1f8bxw1-CcJl",
    "canada_kr_yield_panel_daily_frequency_daily_maturity.parquet":
        "1QQfedXxei8-ByCSjkHftzPIVkjiLCIwu",
    "canada_kr_yield_panel_daily_frequency_monthly_maturity.csv":
        "1cD2goiOFdubPG25wL2E0b3qnh_vQDclx",
    "canada_kr_yield_panel_monthly_frequency_daily_maturity.csv":
        "1ygDxS3b-YLfAO6OLF5zIoWQm5mV8oX7E",
    "canada_kr_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1W4dkToWzs2SIWazlkU09y9qKX6JPA_CY",
    "canada_krt_yield_panel_daily_frequency_daily_maturity.csv":
        "161zeFm_p7ur8_Q2kPZLv_AmPHuqGCVeb",
    "canada_krt_yield_panel_daily_frequency_daily_maturity.parquet":
        "1yxWmkxrGsBkaKU3_q0rgovXPPbir0qwk",
    "canada_krt_yield_panel_daily_frequency_monthly_maturity.csv":
        "1T5nB-xEnIZpv3rL2f8nnCRsSWdObkx-2",
    "canada_krt_yield_panel_monthly_frequency_daily_maturity.csv":
        "1GmN3KCf-LmVQXTPeWsampph-mnxBSsSH",
    "canada_krt_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1D7nIahFAabVY19vj2AWyD_vSYjCSJbHy",
    "detail_canada.csv":
        "1FJwiiYXRZg-jOeSLi_X_cVuthyhKJ9pp",
    "detail_germany.csv":
        "1q2ZY0nwiA2HdUCJqA5kNCY_uSxZqOW-d",
    "detail_japan.csv":
        "1D5YvOj9vHRmb5fZToBbPIJh5gl9N_Irj",
    "detail_switzerland.csv":
        "1LJJwV8ZjqULUL3U8TNq5NGI6V0FDWWNc",
    "detail_united_kingdom.csv":
        "1GoHVzKus0BaLZlz-zW338FD_rQPd_nOJ",
    "germany_kr_yield_panel_daily_frequency_daily_maturity.csv":
        "12WKFjKClPRRuXRkEueEBW5CQDQnVhTfa",
    "germany_kr_yield_panel_daily_frequency_daily_maturity.parquet":
        "1NXfwkHnVRRlzLPBqE9jDJcmdfSgUE2Vw",
    "germany_kr_yield_panel_daily_frequency_monthly_maturity.csv":
        "1sBfwc9tVGkgdfE5aqQDRjIZQ6VXkXw0G",
    "germany_kr_yield_panel_monthly_frequency_daily_maturity.csv":
        "1y_sC1kK77VE3siwWLZ_e7ukvd0OVHMWK",
    "germany_kr_yield_panel_monthly_frequency_monthly_maturity.csv":
        "17DKvqQ8XmeZfoz9APkVNllGAa7fNszho",
    "germany_krt_yield_panel_daily_frequency_daily_maturity.csv":
        "1WAfArmuxcoxnVV9SIw9MRYV9L3HMZeAT",
    "germany_krt_yield_panel_daily_frequency_daily_maturity.parquet":
        "1C4CCcLbujYb9mXJR702O0DZ4hM7x4M3S",
    "germany_krt_yield_panel_daily_frequency_monthly_maturity.csv":
        "1n9DAoc4gO_gBUAWofXcMHKRrxXP-4MN1",
    "germany_krt_yield_panel_monthly_frequency_daily_maturity.csv":
        "1nq93Anp_PlgqWw4A_rWecTztU5i8ne4I",
    "germany_krt_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1P27XIpXVDZNGl0D5UssTWob5lCdy99Ke",
    "japan_kr_yield_panel_daily_frequency_daily_maturity.csv":
        "1xDsBy6COvXn1JobI6ae9EsmkkGwoUxHS",
    "japan_kr_yield_panel_daily_frequency_daily_maturity.parquet":
        "1LoQBHAz0ub00TKgFMRYO-ga4CFWwjAHF",
    "japan_kr_yield_panel_daily_frequency_monthly_maturity.csv":
        "1hDaiao059NnGTpwp5vYGmQ-8SXfPOM6-",
    "japan_kr_yield_panel_monthly_frequency_daily_maturity.csv":
        "1gWRJIBwaiwCR0fxF5h_YPpV2sMJ5X1p6",
    "japan_kr_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1TkBtPON3oWRyCg16OTUXiMNeiIzatDF2",
    "japan_krt_yield_panel_daily_frequency_daily_maturity.csv":
        "1Mp76ed_6PVZiVdF7_xUQ6VJTyejx88Ch",
    "japan_krt_yield_panel_daily_frequency_daily_maturity.parquet":
        "1bssDyxDnwTJrScN49L2gwuWwR3n-9xky",
    "japan_krt_yield_panel_daily_frequency_monthly_maturity.csv":
        "1V1Vh1agu9_MWqn5okIBwhqJuObL22S0u",
    "japan_krt_yield_panel_monthly_frequency_daily_maturity.csv":
        "1igYg7fcN8hTSggb1ez23rSj9siPtizgB",
    "japan_krt_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1ApzmE8-b2IWriMvXOWSKCVnMI-eWYXuh",
    "switzerland_kr_yield_panel_daily_frequency_daily_maturity.csv":
        "1FPVuk5J3JAVL0vMmBPwpFlBV2XZxCC6Y",
    "switzerland_kr_yield_panel_daily_frequency_daily_maturity.parquet":
        "1RcKddqjSquylYppErJbMVWFJebH_ibH3",
    "switzerland_kr_yield_panel_daily_frequency_monthly_maturity.csv":
        "1zBXC9PxhG56M3jHyJNZYBgCZh4Nzj3n8",
    "switzerland_kr_yield_panel_monthly_frequency_daily_maturity.csv":
        "1-r7_R31FZ97tFEUX3HDF5Gbvt1OurcVA",
    "switzerland_kr_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1V_hNjX9Ymu0JAjvUR9TdI3f279t041Rq",
    "switzerland_krt_yield_panel_daily_frequency_daily_maturity.csv":
        "1dlI6IGVn7NUQR5K3F-RUyKFhos0vtPrE",
    "switzerland_krt_yield_panel_daily_frequency_daily_maturity.parquet":
        "1cM4GCR2J5yRdFPhR4ObEydIV5d_yXhEx",
    "switzerland_krt_yield_panel_daily_frequency_monthly_maturity.csv":
        "15rKXwcxL7Wg9nBVtbZfPny6hQOFTp72-",
    "switzerland_krt_yield_panel_monthly_frequency_daily_maturity.csv":
        "1aNKvWh8o37RgA5JK_Ww_PxMMV_09NwlV",
    "switzerland_krt_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1l-PM5BLlCI8Db8ARX9yUG8YTtCVS_YOn",
    "united_states_kr_yield_panel_daily_frequency_daily_maturity.csv":
        "1WYgtuVncBDhbPJ256QmXAFNQLMZXwHVr",
    "united_states_kr_yield_panel_daily_frequency_daily_maturity.parquet":
        "1u86w35VE3541lsVK15TiHGbd4L5ShOda",
    "united_states_kr_yield_panel_daily_frequency_monthly_maturity.csv":
        "19TFAxTnegcmJxSXjEz7nC8peiLABm5MF",
    "united_states_kr_yield_panel_monthly_frequency_daily_maturity.csv":
        "1kR5uQ7pNlt_mURZoLyrObYZ1iTiYBj5Z",
    "united_states_kr_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1MSC9KT8_G18oJKdls9KlLzOeLiagb6gB",
    "united_kingdom_kr_yield_panel_daily_frequency_daily_maturity.csv":
        "1oi4ZiizlcOGaS99GC_InzE8dSoEwK91S",
    "united_kingdom_kr_yield_panel_daily_frequency_daily_maturity.parquet":
        "1kSavMKpsYGRZ6xbDmNu-UP8LBJuLmxiq",
    "united_kingdom_kr_yield_panel_daily_frequency_monthly_maturity.csv":
        "1Z722hOHt2Mq8eCjZpke2125A6vz5iGY_",
    "united_kingdom_kr_yield_panel_monthly_frequency_daily_maturity.csv":
        "1QzkIJe6inBCd3oxZgc_3-ACjVTKak0lr",
    "united_kingdom_kr_yield_panel_monthly_frequency_monthly_maturity.csv":
        "10ZDoBOKrg7U0J1KsYkv-rvdZ1GdUxOQW",
    "united_kingdom_krt_yield_panel_daily_frequency_daily_maturity.csv":
        "1qqDaLGsNlhJlNaGW3ipftrjAbJigTCvo",
    "united_kingdom_krt_yield_panel_daily_frequency_daily_maturity.parquet":
        "1y_ofbvagZxi_yU7MqL3Z0PjYA2YbQcuY",
    "united_kingdom_krt_yield_panel_daily_frequency_monthly_maturity.csv":
        "1aiYmdA2nbhOC0KNOzIp76SKX9_Qd9gA0",
    "united_kingdom_krt_yield_panel_monthly_frequency_daily_maturity.csv":
        "1t2q0NehI1xbfT3cdxj1REeiqeElpRpvM",
    "united_kingdom_krt_yield_panel_monthly_frequency_monthly_maturity.csv":
        "1WxlgrSHVR9Eg6IMcnaKMcUWj76COM56i",
}

# The four variants above, as they appear in the file names.
VARIANT_FILE = ["daily_frequency_daily_maturity",   "daily_frequency_monthly_maturity",
                "monthly_frequency_daily_maturity", "monthly_frequency_monthly_maturity"]
# Page slug -> the market prefix used in the file names.
MARKET_FILE = {"germany": "germany", "japan": "japan", "united-kingdom": "united_kingdom",
               "canada": "canada", "switzerland": "switzerland",
               "united-states": "united_states"}

def panel_rows(slug, method):
    """The four variants of one market's KR or KR-T panel, linked to the Drive files."""
    rows = []
    for label, suffix in zip(VARIANTS, VARIANT_FILE):
        stem = f"{MARKET_FILE[slug]}_{method}_yield_panel_{suffix}"
        links = {"CSV": drive(DRIVE_IDS[stem + ".csv"])}
        if suffix == VARIANT_FILE[0]:
            links["Parquet"] = drive(DRIVE_IDS[stem + ".parquet"])
        rows.append((label, links))
    return rows

def coverage_rows():
    """The bond coverage detail files - international markets only."""
    return [(c["name"], {"CSV": drive(DRIVE_IDS["detail_%s.csv" % MARKET_FILE[slug]])})
            for slug, c in COUNTRIES.items()]

# The U.S. yield panels sit in the same 2026-11-01 folder as the international ones, so they
# use the same helper. The four 2022 Drive files the old site linked to are left untouched.
US_KR = panel_rows("united-states", "kr")

# The other U.S. products are still the Drive files the current site links to, so every
# existing download link keeps working. All verified public and CSV on 2026-09-18.
RISK_FREE = drive("1Cb3Z6PUuJX2K0M1b_CRzIC8V6t9FQSu6")
US_RETURNS = [
    ("Returns, daily maturities",         {"CSV": drive("1Cbxi3qFBI3iqO3RTIZC4ZqjBB02mafKr")}),
    ("Returns, annual maturities",        {"CSV": drive("1CbVXx3ZwS4dk0q035fBooX48r01OV9pa")}),
    ("Risk-free returns",                 {"CSV": RISK_FREE}),
    ("Excess returns, daily maturities",  {"CSV": drive("1Cbutb4-AwCYXxuqyYuwel-vhLrAJ6D5L")}),
    ("Excess returns, annual maturities", {"CSV": drive("1C_TPGQr_sFL5p90JlRDdsyaYlnybkixp")}),
]
US_FACTORS = [
    ("KR-4 factor excess returns", {"CSV": drive("1Caf6Hug6zEyXlK34aMfcdWsEvqcJabPq")}),
    ("Risk-free returns",          {"CSV": RISK_FREE}),
]
US_CONDITIONS = [("IT-VOL and T-COM", {"CSV": drive("1Cbk7ZWpzOIMjfSo71S_50fbAPC_oEl8U")})]

def filelist(rows, cls=""):
    """rows: [(label, {format: url, ...}), ...] - formats are shown in the order given.
    cls=" compact" gives a tight list with no row rules, for short supporting files."""
    out = [f'    <div class="files{cls}">']
    for name, links in rows:
        fm = " ".join(f'<a href="{u}">{f}</a>' for f, u in links.items())
        out.append(f'      <div class="row"><span class="name">{name}</span><span class="fmt">{fm}</span></div>')
    out.append("    </div>")
    return "\n".join(out)

PLACEHOLDER = ""   # download-link annotations removed at the user's request

# --------------------------------------------------------------------------- home
# --------------------------------------------------------------------------- authors
# Names, titles, affiliations and links exactly as on the current site.
AUTHORS = [
    dict(title="Prof. Dr.", name="Damir Filipovic", url="https://www.epfl.ch/labs/csf/",
         aff="Ecole Polytechnique Fédérale de Lausanne (EPFL) and Swiss Finance Institute", photo="filipovic.jpg"),
    dict(title="Prof. Dr.", name="Markus Pelger", url="https://mpelger.people.stanford.edu/",
         aff="Stanford University", photo="pelger.jpg"),
    dict(title="Dr.", name="Ye Ye", url="https://fintech.stanford.edu/people/alumni",
         aff="Uber and Stanford University", photo="ye.jpg"),
    dict(title="", name="Rose Wang", url="https://fintech.stanford.edu/people/doctoral-students",
         aff="Stanford University", photo="wang.jpg"),
]
LOGOS = [
    ("https://www.epfl.ch/en/",      "logo-epfl.png",   "EPFL"),
    ("https://www.sfi.ch/en",        "logo-sfi.jpg",    "Swiss Finance Institute"),
    ("https://fintech.stanford.edu/", "logo-aftlab.png", "Advanced Financial Technologies Laboratory"),
]

def authors_html():
    cards = []
    for a in AUTHORS:
        initials = "".join(w[0] for w in a["name"].split()[:2])
        img = (f'<img src="assets/img/{a["photo"]}" alt="{a["name"]}" loading="lazy">' if a["photo"]
               else f'<div class="ph" aria-hidden="true">{initials}</div>')
        name = f'<a href="{a["url"]}">{a["name"]}</a>' if a["url"] else a["name"]
        title = f'{a["title"]} ' if a["title"] else ""
        cards.append(f'      <div class="author">{img}<p class="aname">{title}{name}</p>'
                     f'<p class="aff">{a["aff"]}</p></div>')
    logos = "\n".join(f'      <a href="{u}"><img src="assets/img/{f}" alt="{alt}"></a>' for u, f, alt in LOGOS)
    return ('    <h2 id="authors">Authors</h2>\n    <div class="authors">\n' + "\n".join(cards) +
            '\n    </div>\n    <div class="logos">\n' + logos + '\n    </div>\n')

# Home: one compact card per market. Whole card is the link; the dataset summary is always visible.
HOME_CARDS = [
    # Two deliberate lines, so the U.S. summary never breaks in an arbitrary place
    ("united-states.html",   "United States",  "KR yields · Returns · Factors<br><span class=\"nb\">Market conditions</span>"),
    ("germany.html",         "Germany",        "KR yields · KR-T yields"),
    ("japan.html",           "Japan",          "KR yields · KR-T yields"),
    ("united-kingdom.html",  "United Kingdom", "KR yields · KR-T yields"),
    ("canada.html",          "Canada",         "KR yields · KR-T yields"),
    ("switzerland.html",     "Switzerland",    "KR yields · KR-T yields"),
]

def country_cards():
    out = ['    <div class="countries">']
    for href, name, data in HOME_CARDS:
        out.append(f'      <a class="ccard" href="{href}"><span class="cname">{name}</span>'
                   f'<span class="cdata">{data}</span>'
                   f'<span class="cgo" aria-hidden="true">View data &rarr;</span></a>')
    out.append("    </div>")
    return "\n".join(out)

home = f"""    <p>This website provides government zero-coupon yield curve estimates for the United States,
    Germany, Japan, the United Kingdom, Canada, and Switzerland. All six markets include Kernel Ridge
    Regression (KR) yield curves. For the five non-U.S. markets, KR-Transfer (KR-T) estimates additionally
    incorporate information from U.S. Treasury and foreign-exchange markets. The United States page also
    provides discount bond returns, term structure factors, and bond market condition measures.</p>

    <p class="statement">Across all six markets, we show in an extensive empirical study that our method
    strongly dominates all parametric and non-parametric benchmarks. Our method achieves substantially
    smaller out-of-sample yield and pricing errors, while being robust to outliers and data selection
    choices. We attribute the superior performance to the optimal trade-off between flexibility and
    smoothness, which positions our method as the new standard for yield curve estimation.</p>

    <h2>Data by country</h2>
{country_cards()}

    <h2 id="methods">Methods</h2>
    <div class="cols2">
      <div>
        <h3>Kernel Ridge Regression (KR)</h3>
        <p>KR estimates a market's discount curve from that market's own government bonds. Rather than
        imposing a parametric shape, it searches a general class of smooth curves and trades off how well
        the curve reprices the observed bonds against how much curvature it needs to do so. The penalty
        applies to curvature only, so the level and slope of the curve are left to the data.</p>
        <p>Available for all six markets.</p>
      </div>
      <div>
        <h3>KR-Transfer (KR-T)</h3>
        <p>Local bond markets have maturity gaps. KR-T fills them using the deepest market available: FX
        spot and forward rates convert U.S. Treasuries into target-currency synthetic bonds, and the two
        curves are estimated jointly under a weak covered-interest-parity restriction that penalises only
        the curvature of the cross-currency spread.</p>
        <p>Available for the five non-U.S. markets.</p>
      </div>
    </div>
    <p style="margin-top:14px"><strong>Which one?</strong> The two agree closely at maturities where local
    government bonds are densely observed. KR-T is the better choice where the local cross-section is
    sparse. <a href="faq.html#accuracy">See the empirical evidence →</a></p>

    <h2>Research</h2>
    <p class="small left" style="margin-bottom:14px">The database is documented in three papers. Cite the
    one matching the data you use (<a href="methodology.html#cite">how to cite</a>).</p>
    <details>
      <summary>Stripping the Discount Curve - a Robust Machine Learning Approach</summary>
      <div class="body">
        <p class="cite">Damir Filipovic, Markus Pelger &amp; Ye Ye · <em>Management Science</em>, 2026</p>
        <p>Introduces the kernel ridge regression approach to discount curve estimation and shows that it
        dominates parametric and nonparametric benchmarks for U.S. Treasuries. This is the methodology
        behind the KR yield curves.</p>
        <p><a href="https://doi.org/10.1287/mnsc.2023.01401">Management Science →</a> · <a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4058150">SSRN →</a></p>
      </div>
    </details>
    <details>
      <summary>Shrinking the Term Structure</summary>
      <div class="body">
        <p class="cite">Damir Filipovic, Markus Pelger &amp; Ye Ye · <em>Review of Finance</em>, 2026</p>
        <p>Shows that the same framework unifies curve estimation with cross-sectional factor modelling,
        and identifies a fourth &ldquo;complexity&rdquo; factor carrying a large risk premium. This is the
        methodology behind the U.S. discount bond returns, term structure factors, and bond market
        condition measures.</p>
        <p><a href="https://doi.org/10.1093/rof/rfag033">Review of Finance →</a> · <a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4182649">SSRN →</a></p>
      </div>
    </details>
    <details>
      <summary>Stripping Discount Curves Across Currencies: Transfer Learning from US Treasuries</summary>
      <div class="body">
        <p class="cite">Damir Filipovic, Markus Pelger &amp; Rose Wang · Working paper, 2026</p>
        <p>Shows that KR generalises to all six government bond markets and uniformly dominates the
        Nelson-Siegel-Svensson benchmark, then introduces KR-T, a transfer-learning extension that carries
        information from data-rich to data-poor markets through FX forwards. This is the methodology behind
        the KR-T yield curves.</p>
        <p><a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7092381">SSRN →</a></p>
      </div>
    </details>

{authors_html()}
"""

pages = {"index.html": ("Discount Bond Database", home)}

# --------------------------------------------------------------------------- country pages
for slug, c in COUNTRIES.items():
    kr_start, kr_n = c["kr"]; krt_start, krt_n = c["krt"]
    body = f"""    <h1 class="page">{c['name']}</h1>
    <p class="lede">Government zero-coupon yield curve estimates for {c['name']}.</p>

    <div class="glance">
      <span class="glance-label">At a glance</span>
      <dl class="facts">
        <dt>KR yields</dt><dd>{kr_start} - {END}</dd>
        <dt>KR-T yields</dt><dd>{krt_start} - {END}</dd>
        <dt>Maturities</dt><dd>Daily maturities to {c['max_day']} days ({c['max_year']} years); monthly maturities to {c['max_month']} months</dd>
        <dt>Yields</dt><dd>Annualized, continuously compounded · decimal · 365-day year</dd>
      </dl>
    </div>

    <p class="callout"><strong>Choosing between them.</strong> The two estimates agree closely at
    maturities where {c['adj']} government bonds are densely observed. Where the local cross-section is
    sparse, KR-T is the better choice, because it also draws on the U.S. reference market through FX.
    <a href="index.html#methods">More on the methods &rarr;</a></p>

    <div class="dataset">
      <div class="sechead"><h2>KR yields</h2>
        <a class="details" href="details-kr-yields.html">Details and file format &rarr;</a></div>
      <p class="left">Standalone Kernel Ridge Regression estimates using {c['adj']} government bonds.{cite('paper-krt', 'KR yields')}</p>
{filelist(panel_rows(slug, "kr"))}
    </div>

    <div class="dataset">
      <div class="sechead"><h2>KR-T yields</h2>
        <a class="details" href="details-krt-yields.html">Details and file format &rarr;</a></div>
      <p class="left">Transfer-learning estimates incorporating information from the U.S. Treasury and
      foreign-exchange markets.{cite('paper-krt', 'KR-T yields')}</p>
{filelist(panel_rows(slug, "krt"))}
    </div>

    <p class="support"><a href="methodology.html#coverage">Bond counts, observed maturity range, and
    date inclusion details &rarr;</a></p>
"""
    pages[f"{slug}.html"] = (f"{c['name']} | Discount Bond Database", body)

# --------------------------------------------------------------------------- united states
us_body = f"""    <h1 class="page">United States</h1>
    <p class="lede">U.S. Treasury yield curves, discount bond returns, term structure factors, and bond
    market condition measures.</p>

    <div class="glance">
      <span class="glance-label">At a glance</span>
      <dl class="facts">
        <dt>Coverage</dt><dd>June 14, 1961 - June 30, 2025</dd>
        <dt>Maturities</dt><dd>Daily maturities to 10,950 days (30 years); monthly maturities to 360 months</dd>
        <dt>Yields</dt><dd>Annualized, continuously compounded · decimal · 365-day year</dd>
        <dt>Returns</dt><dd>One-business-day returns · maturities to 10 years</dd>
      </dl>
    </div>

    <div class="dataset">
      <div class="sechead"><h2>KR yields</h2>
        <a class="details" href="details-us-yields.html">Details and file format &rarr;</a></div>
      <p class="left">Kernel Ridge Regression zero-coupon yield curves for U.S. Treasuries. 10-, 20-, and
      30-year estimates begin on June 14, 1961, January 5, 1973, and November 25, 1985, respectively.{cite('paper-kr', 'KR yields')}</p>
{filelist(US_KR)}
      <details class="notice">
        <summary><span class="nmsg">Yield file layout changed in October 2026.</span><span class="nmore">Details &rarr;</span></summary>
        <div class="body"><p>The yield values are unchanged. The files now use <code>date</code>,
        <code>min_observed_ttm</code>, <code>max_observed_ttm</code> and <code>max_curve_ttm</code> before
        the maturity columns. The old <code>MAX_DATA_TTM</code> column has been removed.
        <a href="details-us-yields.html">Full file documentation &rarr;</a></p></div>
      </details>
    </div>

    <div class="dataset">
      <div class="sechead"><h2>Discount bond returns</h2>
        <a class="details" href="details-us-returns.html">Details and file format &rarr;</a></div>
      <p class="left">Daily returns and excess returns of zero-coupon bonds, constructed as tradable
      portfolios of U.S. Treasuries. This dataset and the two below are based on
      <em>Shrinking the Term Structure</em>.{cite('paper-factors', 'Discount bond returns')}</p>
{filelist(US_RETURNS)}
    </div>

    <div class="dataset">
      <div class="sechead"><h2>Term structure factors</h2>
        <a class="details" href="details-us-factors.html">Details and file format &rarr;</a></div>
      <p class="left">The four KR-4 factors provide an excellent representation of the discount bond excess
      return curve. When modelling discount returns rather than excess returns, the risk-free returns
      should be added.</p>
{filelist(US_FACTORS)}
    </div>

    <div class="dataset">
      <div class="sechead"><h2>Bond market condition measures</h2>
        <a class="details" href="details-us-conditions.html">Details and file format &rarr;</a></div>
      <p class="left">Idiosyncratic Treasury Volatility (IT-VOL) measures idiosyncratic volatility
      normalised by overall volatility. Treasury Market Complexity (T-COM) measures the complexity of the
      term structure.</p>
{filelist(US_CONDITIONS)}
    </div>
{PLACEHOLDER}
"""
pages["united-states.html"] = ("United States | Discount Bond Database", us_body)

# --------------------------------------------------------------------------- dataset detail pages
# One page per dataset, in the spirit of the Ken French "Details" pages: what it contains,
# how it is built, and how to read the files. Shared material stays on methodology.html.

STAT_TIPS = {
    "published":           "Included in panel",
    "holiday":             "Domestic Bloomberg holiday",
    "holiday_domestic":    "Domestic Bloomberg holiday",
    "few_bonds":           "&lt; 5 domestic bonds",
    "no_us_data":          "U.S. holiday or market closure",
    "no_fx_spot":          "FX spot unavailable",
    "no_fx_forward":       "FX forward unavailable",
    "fx_input_inadequate": "FX quotes inadequate",
}

def stat(code):
    ref = "def-holiday" if code.startswith("holiday") else f"def-{code}"
    return (f'<span class="stat" tabindex="0" aria-describedby="{ref}" '
            f'data-tip="{STAT_TIPS[code]}">{code}</span>')

KR_VALUES  = ", ".join(stat(c) for c in ["published", "holiday", "few_bonds"])
KRT_VALUES = ", ".join(stat(c) for c in ["published", "holiday_domestic", "few_bonds",
                                         "no_us_data", "no_fx_spot", "no_fx_forward",
                                         "fx_input_inadequate"])

DATASETS = [
    ("details-kr-yields.html",      "KR yields",                        "International markets"),
    ("details-krt-yields.html",     "KR-T yields",                      "International markets"),
    ("details-us-yields.html",      "KR yields",                        "United States"),
    ("details-us-returns.html",     "Discount bond returns",            "United States"),
    ("details-us-factors.html",     "Term structure factors",           "United States"),
    ("details-us-conditions.html",  "Bond market condition measures",   "United States"),
]

INTL_MARKET_LINKS = " · ".join(f'<a href="{s}.html">{c["name"]}</a>' for s, c in COUNTRIES.items())

def detail(title, scope, lede, body):
    return f"""    <p class="crumb"><a href="methodology.html">Data Documentation &amp; Code</a>
    &rsaquo; {scope}</p>
    <h1 class="page">{title}</h1>
    <p class="lede">{lede}</p>
{body}"""

pages["details-kr-yields.html"] = ("KR yields, international markets | Discount Bond Database", detail(
    "KR yields", "International markets",
    "Standalone Kernel Ridge Regression zero-coupon yield curves for Germany, Japan, the United "
    "Kingdom, Canada and Switzerland, each fitted to that market's own government bonds.", """
    <h2>File format and coverage</h2>
    <p>All yield files begin with <code>date</code>, <code>min_observed_ttm</code>,
    <code>max_observed_ttm</code> and <code>max_curve_ttm</code> - <code>_days</code> in
    daily-maturity files, <code>_months</code> in monthly-maturity files - followed by one column per
    maturity.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
        <tbody>
          <tr><td><code>date</code></td><td>Observation date (<code>YYYY-MM-DD</code>)</td></tr>
          <tr><td><code>min_observed_ttm_days</code> / <code>_months</code></td>
              <td>Shortest maturity in that day's fitted bond cross-section</td></tr>
          <tr><td><code>max_observed_ttm_days</code> / <code>_months</code></td>
              <td>Longest maturity in that cross-section</td></tr>
          <tr><td><code>max_curve_ttm_days</code> / <code>_months</code></td>
              <td>Last maturity with a published KR value; the upper endpoint is that day's longest
              observed domestic bond, <code>max_observed_ttm</code></td></tr>
        </tbody>
      </table>
    </div>
    <p style="margin-top:12px">Yields are annualized, continuously compounded, on a 365-day year, in
    decimal units, and cells past <code>max_curve_ttm</code> are blank. Every variant is published as
    CSV; the daily-observations, daily-maturities variant is also published as Parquet, with the same
    columns.</p>

    <h2>Data availability</h2>
    <p>The government bond quotes come from Bloomberg. A date is published when the market has at least
    five domestic bonds and is not a Bloomberg holiday, so the sample starts later in markets whose
    early cross-section is thin. Date-level inclusion and exclusion reasons, and the bond count behind
    each date, are in the <a href="methodology.html#coverage">bond coverage detail files</a>; each
    market's own date range is on its country page.</p>

    <h2>Construction</h2>
    <p>KR estimates the discount curve from that market's own government bonds, with no information
    from any other market. Rather than imposing a parametric shape it searches a general class of
    smooth curves, trading off how well the curve reprices the observed bonds against how much
    curvature it needs to do so, so the level and slope of the curve are left to the data. Estimation
    is independent across markets and across dates.</p>
    <p class="ref"><em>Stripping Discount Curves Across Currencies: Transfer Learning from US
    Treasuries</em> &middot; <a href="methodology.html#paper-krt">Paper &amp; citation &rarr;</a></p>
"""))

pages["details-krt-yields.html"] = ("KR-T yields, international markets | Discount Bond Database", detail(
    "KR-T yields", "International markets",
    "Transfer-learning zero-coupon yield curves for Germany, Japan, the United Kingdom, Canada and "
    "Switzerland, jointly estimated with U.S. Treasuries.", """
    <h2>File format and coverage</h2>
    <p>All yield files begin with <code>date</code>, <code>min_observed_ttm</code>,
    <code>max_observed_ttm</code> and <code>max_curve_ttm</code> - <code>_days</code> in
    daily-maturity files, <code>_months</code> in monthly-maturity files - followed by one column per
    maturity.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
        <tbody>
          <tr><td><code>date</code></td><td>Observation date (<code>YYYY-MM-DD</code>)</td></tr>
          <tr><td><code>min_observed_ttm_days</code> / <code>_months</code></td>
              <td>Shortest maturity of the domestic bonds used in estimation on that date</td></tr>
          <tr><td><code>max_observed_ttm_days</code> / <code>_months</code></td>
              <td>Longest maturity of the domestic bonds used in estimation on that date</td></tr>
          <tr><td><code>max_curve_ttm_days</code> / <code>_months</code></td>
              <td>Last maturity with a published KR-T value: the endpoint of the curve actually
              published on that date</td></tr>
        </tbody>
      </table>
    </div>
    <p>On each date, KR-T yields are published only up to the last maturity supported by an observed domestic bond or a synthetic bond priced using FX forwards within the observed FX forward range.</p>
    <p style="margin-top:12px">Yields are annualized, continuously compounded, on a 365-day year, in
    decimal units, and cells past <code>max_curve_ttm</code> are blank. Every variant is published as
    CSV; the daily-observations, daily-maturities variant is also published as Parquet, with the same
    columns.</p>

    <h2>Data availability</h2>
    <p>A date is published only when domestic bond data, U.S. reference data, FX spot and FX forward
    quotes are all available, so the KR-T dates for a market can differ from its KR dates. The
    international government bond quotes and the FX spot and forward rates come from Bloomberg.
    Date-level inclusion and exclusion reasons are available in the
    <a href="methodology.html#coverage">bond coverage detail files</a>.</p>

    <h2>Construction</h2>
    <p>Local bond markets have maturity gaps: on many dates no domestic bond sits near the maturity of
    interest. KR-T fills them from the deepest market available. U.S. Treasuries are converted into the
    local currency through FX spot and forward rates, and the domestic and converted bonds are fitted
    jointly, under a penalty on the curvature of the cross-currency spread that leaves its level and
    slope free. Where the domestic cross-section is already dense, KR-T reproduces standalone KR.</p>
    <p class="ref"><em>Stripping Discount Curves Across Currencies: Transfer Learning from US
    Treasuries</em> &middot; <a href="methodology.html#paper-krt">Paper &amp; citation &rarr;</a></p>
"""))

pages["details-us-yields.html"] = ("U.S. KR yields | Discount Bond Database", detail(
    "U.S. KR yields", "United States",
    "Kernel Ridge Regression zero-coupon yield curves for U.S. Treasuries, the reference dataset behind "
    "the U.S. discount bond database.", """
    <h2>File format and coverage</h2>
    <p>All yield files begin with <code>date</code>, <code>min_observed_ttm</code>,
    <code>max_observed_ttm</code> and <code>max_curve_ttm</code> - <code>_days</code> in
    daily-maturity files, <code>_months</code> in monthly-maturity files - followed by one column per
    maturity.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
        <tbody>
          <tr><td><code>date</code></td><td>Observation date (<code>YYYY-MM-DD</code>)</td></tr>
          <tr><td><code>min_observed_ttm_days</code> / <code>_months</code></td>
              <td>Shortest maturity among the Treasuries observed that day</td></tr>
          <tr><td><code>max_observed_ttm_days</code> / <code>_months</code></td>
              <td>Longest maturity among those Treasuries; the boundary of the extrapolation region</td></tr>
          <tr><td><code>max_curve_ttm_days</code> / <code>_months</code></td>
              <td>Last maturity with a published value; it follows the U.S. publication horizon, which
              steps 3,650 &rarr; 7,300 &rarr; 10,950 days across vintages, and so need not coincide with
              <code>max_observed_ttm</code> in either direction</td></tr>
        </tbody>
      </table>
    </div>
    <p style="margin-top:12px">Yields are annualized, continuously compounded, on a 365-day year, in
    decimal units, and cells past <code>max_curve_ttm</code> are blank. Every variant is published as
    CSV; the daily-observations, daily-maturities variant is also published as Parquet, with the same
    columns.</p>
    <details class="notice">
      <summary><span class="nmsg">Yield file layout changed in October 2026.</span><span class="nmore">Details &rarr;</span></summary>
      <div class="body"><p>The yield values are unchanged. The files now use the four columns above, the
      same layout as the international panels. The old <code>MAX_DATA_TTM</code> column has been
      removed; <code>max_observed_ttm</code> replaces it.</p></div>
    </details>

    <h2>Data availability</h2>
    <p>Daily from June 14, 1961, on the U.S. Treasury trading calendar; the international date filter is
    not applied and no bond coverage detail file is published for the United States. 10-, 20-, and
    30-year estimates begin on June 14, 1961, January 5, 1973, and November 25, 1985, respectively.
    Treasury data come from the CRSP Treasuries Time Series.</p>

    <h2>Construction</h2>
    <p>KR estimates the discount curve from observed U.S. Treasury prices, trading off repricing fit
    against curvature, and the published values are the previously released U.S. estimates carried over
    unchanged. This is a different pipeline from the international panels, with its own ridge scaling:
    the two share a file format and a yield convention, not an estimation run.</p>
    <p class="ref"><em>Stripping the Discount Curve - a Robust Machine Learning Approach</em> &middot;
    <a href="methodology.html#paper-kr">Paper &amp; citation &rarr;</a></p>
"""))

pages["details-us-returns.html"] = ("U.S. discount bond returns | Discount Bond Database", detail(
    "U.S. discount bond returns", "United States",
    "Daily returns and excess returns of zero-coupon bonds, which are tradable portfolios of U.S. "
    "Treasuries.", """
    <h2>File format</h2>
    <p>Each file begins with the observation date, followed by one column per maturity. Five files are
    published, all CSV.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>File</th><th>Columns</th></tr></thead>
        <tbody>
          <tr><td>Returns, daily maturities</td><td>Date, then one column per day of maturity</td></tr>
          <tr><td>Returns, annual maturities</td><td>Date, then <code>1-yr</code> … <code>10-yr</code></td></tr>
          <tr><td>Excess returns, daily maturities</td><td>Date, then one column per day of maturity</td></tr>
          <tr><td>Excess returns, annual maturities</td><td>Date, then <code>1-yr</code> … <code>10-yr</code></td></tr>
          <tr><td>Risk-free returns</td><td>Date, then <code>One-period risk-free rate</code></td></tr>
        </tbody>
      </table>
    </div>
    <p style="margin-top:12px">The date column carries no header text, so a reader that names columns
    from the header row will leave it unnamed. Dates are <code>YYYY-MM-DD</code>.</p>

    <h2>Data availability</h2>
    <p>Daily from June 14, 1961, with maturities up to ten years. Returns at daily frequency are
    one-business-day returns on the usual 365-day year: the return on day <em>t</em> is the return
    relative to business day <em>t</em>+1. Excess returns are returns minus the risk-free return.</p>

    <h2>Construction</h2>
    <p>The zero-coupon bonds are tradable portfolios of U.S. Treasuries, formed within the same
    reproducing-kernel framework that estimates the curve, so the returns are those of investable
    positions rather than of a fitted curve. The risk-free return is the one-day rate read off the
    estimated discount curve, compounded over the days between consecutive business days.</p>
    <p class="ref"><em>Shrinking the Term Structure</em> &middot;
    <a href="methodology.html#paper-factors">Paper &amp; citation &rarr;</a> &middot; the risk-free
    return is from <em>Stripping the Discount Curve</em>
    (<a href="methodology.html#paper-kr">paper &amp; citation</a>)</p>
"""))

pages["details-us-factors.html"] = ("U.S. term structure factors | Discount Bond Database", detail(
    "U.S. term structure factors", "United States",
    "Daily excess returns of the four KR-4 factors, which provide an excellent representation of the "
    "discount bond excess return curve.", """
    <h2>File format</h2>
    <p>Two CSV files: the factor excess returns, and the risk-free returns published with the
    <a href="details-us-returns.html">discount bond returns</a>.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>File</th><th>Columns</th></tr></thead>
        <tbody>
          <tr><td>KR-4 factor excess returns</td><td>Date, then factors <code>1</code> … <code>4</code></td></tr>
          <tr><td>Risk-free returns</td><td>Date, then <code>One-period risk-free rate</code></td></tr>
        </tbody>
      </table>
    </div>
    <p style="margin-top:12px">The date column carries no header text. Dates are
    <code>YYYY-MM-DD</code>.</p>

    <h2>Data availability</h2>
    <p>Daily from June 14, 1961, alongside the daily risk-free returns.</p>

    <h2>Construction</h2>
    <p>The four factors are investable portfolios of traded assets that replicate the term structure
    and are sufficient to hedge against interest rate changes. They are published as excess returns,
    which remove the risk-free level from discount returns; adding the risk-free returns back gives a
    five-factor representation of discount returns.</p>
    <p class="ref"><em>Shrinking the Term Structure</em> &middot;
    <a href="methodology.html#paper-factors">Paper &amp; citation &rarr;</a></p>
"""))

pages["details-us-conditions.html"] = ("U.S. bond market condition measures | Discount Bond Database", detail(
    "U.S. bond market condition measures", "United States",
    "Two daily measures of the state of the U.S. Treasury market: Idiosyncratic Treasury Volatility "
    "(IT-VOL) and Treasury Market Complexity (T-COM).", """
    <h2>File format</h2>
    <p>One CSV file carrying both measures.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Column</th><th>Meaning</th></tr></thead>
        <tbody>
          <tr><td>Date</td><td>Observation date (<code>YYYY-MM-DD</code>), no header text</td></tr>
          <tr><td><code>IT-VOL</code></td><td>Idiosyncratic Treasury Volatility</td></tr>
          <tr><td><code>T-COM</code></td><td>Treasury Market Complexity</td></tr>
        </tbody>
      </table>
    </div>

    <h2>Data availability</h2>
    <p>Daily from June 14, 1961.</p>

    <h2>Construction</h2>
    <p>Both measures are built from the exposure of Treasury returns to the
    <a href="details-us-factors.html">term structure factors</a>, whose explanatory power varies over
    time. IT-VOL is idiosyncratic volatility normalised by overall volatility: how hard the observed
    bond returns are to explain even with a flexible model. T-COM measures how much variation is
    explained by higher-order factors. Both are strongly related to the term structure risk
    premium.</p>
    <p class="ref"><em>Shrinking the Term Structure</em> &middot;
    <a href="methodology.html#paper-factors">Paper &amp; citation &rarr;</a></p>
"""))

# --------------------------------------------------------------------------- methodology
meth = """    <h1 class="page">Data Documentation &amp; Code</h1>
    <div class="pagenav">
      <div class="nrow"><span class="lab">Data docs</span>
        <span class="items"><a href="#conventions">Conventions</a> &middot;
        <a href="#sources">Sources &amp; sample construction</a></span></div>
      <div class="nrow"><span class="lab">Reference</span>
        <span class="items"><a href="#code">Code</a> &middot;
        <a href="#cite">Papers &amp; citations</a></span></div>
    </div>

    <h2 id="conventions">Terms and conventions</h2>
    <p>All yield files begin with <code>date</code> and the three coverage fields, followed by one
    column per maturity. Daily-maturity files use <code>_days</code>; monthly-maturity files use
    <code>_months</code>.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
        <tbody>
          <tr><td><code>date</code></td><td>Observation date (<code>YYYY-MM-DD</code>)</td></tr>
          <tr><td><code>min_observed_ttm_days</code> / <code>_months</code></td>
              <td>Shortest remaining maturity in that day's fitted bond cross-section</td></tr>
          <tr><td><code>max_observed_ttm_days</code> / <code>_months</code></td>
              <td>Longest remaining maturity in that cross-section</td></tr>
          <tr><td><code>max_curve_ttm_days</code> / <code>_months</code></td>
              <td>Last maturity with a published curve value on that date</td></tr>
        </tbody>
      </table>
    </div>
    <p style="margin-top:12px">Monthly-observation files use the last available published date of each
    calendar month; monthly-maturity files report maturities
    <a href="faq.html#monthly-maturities">in months</a>. For standalone
    <a href="details-kr-yields.html">KR</a> in Germany, Japan, the United Kingdom, Canada and
    Switzerland, <code>max_curve_ttm_days</code> / <code>_months</code> coincides with
    <code>max_observed_ttm_days</code> / <code>_months</code>.
    <a href="details-krt-yields.html">KR-T</a> for those markets may extend further, where an
    FX-transformed U.S. Treasury reaches beyond the longest domestic bond. For
    <a href="details-us-yields.html">U.S. KR</a>, <code>max_curve_ttm_days</code> / <code>_months</code>
    follows the publication horizon and therefore need not coincide with
    <code>max_observed_ttm_days</code> / <code>_months</code>.</p>

    <h2 id="sources">Data sources and sample construction</h2>
    <h3>Sources</h3>
    <p>U.S. Treasury data come from the CRSP Treasuries Time Series. Government bond data for Germany,
    Japan, the United Kingdom, Canada, and Switzerland, together with the corresponding FX spot and
    forward rates, come from Bloomberg using the composite BGN pricing source.</p>

    <h3>Bond filters</h3>
    <ul class="bullets">
      <li>Bonds within about three months of maturity excluded, on liquidity grounds</li>
      <li>Callable / sinkable / puttable / perpetual / convertible / floating-rate / fungible securities
      excluded</li>
      <li>Outlier quotes excluded, where the yield deviates sharply from that day's cross-sectional
      median</li>
      <li>U.S. on-the-run issues excluded, for their liquidity and specialness</li>
      <li>U.K. gilts excluded within the ex-dividend window before a coupon date, where accrued interest
      turns negative, and during partly-paid issuance periods</li>
      <li>Swiss Treasury bills excluded, as the source returns almost no quotes for them</li>
    </ul>

    <h3 id="coverage">Coverage and date inclusion</h3>
    <p>International KR panels exclude domestic Bloomberg holidays and dates with fewer than five
    domestic bonds. KR-T additionally requires U.S. reference data and FX spot and forward data. For
    date-level bond counts, observed maturity coverage, and the reason a date is included or excluded,
    see the bond coverage detail files below.</p>
<!--COVERAGE_FILES-->
    <details class="fields">
      <summary>Field definitions</summary>
      <div class="body">
        <div class="tablewrap">
          <table>
            <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
            <tbody>
              <tr><td><code>date</code></td><td>Observation date (<code>YYYY-MM-DD</code>)</td></tr>
              <tr><td><code>n_bonds</code></td><td>Bonds entering that day's fitted cross-section, after
                  the screens above</td></tr>
              <tr><td><code>min_observed_ttm_days</code></td><td>Shortest remaining maturity among those bonds</td></tr>
              <tr><td><code>max_observed_ttm_days</code></td><td>Longest remaining maturity among those bonds</td></tr>
              <tr><td><code>kr_status</code></td><td>Whether the date is included in the KR panel.
                  Values: <!--KR_VALUES--></td></tr>
              <tr><td><code>krt_status</code></td><td>Whether the date is included in the KR-T panel.
                  Values: <!--KRT_VALUES--></td></tr>
            </tbody>
          </table>
        </div>
        <ul class="defs">
          <li id="def-published"><code>published</code>: the date is in that panel.</li>
          <li id="def-holiday"><code>holiday</code> (KR) / <code>holiday_domestic</code> (KR-T):
          Bloomberg holiday in the domestic market.</li>
          <li id="def-few_bonds"><code>few_bonds</code>: fewer than five domestic bonds that day.</li>
          <li id="def-no_us_data"><code>no_us_data</code>: U.S. reference data unavailable, a U.S.
          holiday or market closure.</li>
          <li id="def-no_fx_spot"><code>no_fx_spot</code>: FX spot rate missing although forwards
          exist.</li>
          <li id="def-no_fx_forward"><code>no_fx_forward</code>: no FX forward quote for that currency
          that day.</li>
          <li id="def-fx_input_inadequate"><code>fx_input_inadequate</code>: the observed FX quotes do
          not support the short end (0.06% of KR-T dates).
          <a href="faq.html#krt-date-range">How these quotes are identified &rarr;</a></li>
        </ul>
      </div>
    </details>

    <h2 id="code">Code</h2>
    <div class="files">
      <div class="row"><span class="name">U.S. discount curve and yield estimation</span>
        <span class="fmt"><a href="https://github.com/yye9701/KR_example">github.com/yye9701/KR_example</a></span></div>
      <div class="row"><span class="name">U.S. returns and factor estimation</span>
        <span class="fmt"><a href="https://github.com/rosieiiiii/KR_return_example">github.com/rosieiiiii/KR_return_example</a></span></div>
      <div class="row"><span class="name">International KR and KR-T estimation</span>
        <span class="fmt" style="color:var(--faint)">Coming soon</span></div>
    </div>

    <h2 id="cite">Papers and how to cite</h2>
    <p>The data are free to use, provided the corresponding paper is cited.</p>
    <details id="paper-kr" style="margin-top:18px">
      <summary>Stripping the Discount Curve - a Robust Machine Learning Approach</summary>
      <div class="body">
        <p class="cite">Damir Filipovic, Markus Pelger &amp; Ye Ye · <em>Management Science</em> 72(9), 8057-8120, 2026</p>
        <p>Introduces the kernel ridge regression approach to discount curve estimation. Methodology for
        the KR yield curves and the risk-free return.</p>
        <p class="citelinks"><a href="https://doi.org/10.1287/mnsc.2023.01401">DOI</a> &middot;
        <a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4058150">SSRN</a> &middot;
        <button type="button" class="copy" data-cite="paper-kr" data-kind="text">Copy citation</button> &middot;
        <button type="button" class="copy" data-cite="paper-kr" data-kind="bibtex">BibTeX</button></p>
      </div>
    </details>
    <details id="paper-factors">
      <summary>Shrinking the Term Structure</summary>
      <div class="body">
        <p class="cite">Damir Filipovic, Markus Pelger &amp; Ye Ye · <em>Review of Finance</em>, advance article, 2026</p>
        <p>Unifies curve estimation with cross-sectional factor modelling and identifies a fourth
        complexity factor. Methodology for the U.S. discount bond returns, term structure factors and
        bond market condition measures.</p>
        <p class="citelinks"><a href="https://doi.org/10.1093/rof/rfag033">DOI</a> &middot;
        <a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4182649">SSRN</a> &middot;
        <button type="button" class="copy" data-cite="paper-factors" data-kind="text">Copy citation</button> &middot;
        <button type="button" class="copy" data-cite="paper-factors" data-kind="bibtex">BibTeX</button></p>
      </div>
    </details>
    <details id="paper-krt">
      <summary>Stripping Discount Curves Across Currencies: Transfer Learning from US Treasuries</summary>
      <div class="body">
        <p class="cite">Damir Filipovic, Markus Pelger &amp; Rose Wang · Working paper, 2026</p>
        <p>Extends KR to six government bond markets and introduces KR-T, which carries information from
        data-rich to data-poor markets through FX forwards. Methodology for the international KR and
        KR-T yield curves.</p>
        <p class="citelinks"><a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7092381">SSRN</a> &middot;
        <button type="button" class="copy" data-cite="paper-krt" data-kind="text">Copy citation</button> &middot;
        <button type="button" class="copy" data-cite="paper-krt" data-kind="bibtex">BibTeX</button></p>
      </div>
    </details>
    <p style="margin-top:16px"><a href="citations.bib" download>Download all three citations as BibTeX (citations.bib) &rarr;</a></p>
"""
meth = meth.replace("<!--COVERAGE_FILES-->", filelist(coverage_rows(), " compact"))
meth = meth.replace("<!--KR_VALUES-->", KR_VALUES).replace("<!--KRT_VALUES-->", KRT_VALUES)
pages["methodology.html"] = ("Data Documentation & Code | Discount Bond Database", meth)

# --------------------------------------------------------------------------- faq
def qa(q, a, anchor=None):
    """anchor -> a stable id, so other pages can link straight to one question."""
    aid = f' id="{anchor}"' if anchor else ""
    return f"    <details{aid}>\n      <summary>{q}</summary>\n      <div class=\"body\">{a}</div>\n    </details>"

faq = """    <h1 class="page">Frequently Asked Questions</h1>
    <p class="lede">Practical information for using and interpreting the Discount Bond Database.</p>

    <h2>General</h2>
""" + "\n".join([
 qa("How are monthly maturities defined?",
    "<p>For maturities from 1 to 12 months, the number of days in <em>i</em> month(s) is calculated as "
    "365 × <em>i</em> / 12, rounded to the nearest integer - giving 30, 61, 91, 122, 152, 183, 213, 243, "
    "274, 304, 335 and 365 days.</p>", "monthly-maturities"),
 qa("What day-count convention is used?",
    "<p>The usual convention of 365 days in each year. Because the data are provided at daily maturity "
    "resolution, users can apply an alternative convention if they prefer.</p>", "day-count"),
 qa("Should I use KR or KR-T?",
    "<p>It depends on how densely the local bond market is observed at the maturities you care about. "
    "Where domestic bonds are plentiful, the two estimates agree closely and either can be used. Where the "
    "local cross-section is sparse, KR-T is the better choice, because it draws additional information "
    "from the U.S. reference market through FX spot and forward rates.</p>", "kr-or-krt"),
 qa("How accurate are these estimates compared with standard methods?",
    "<p>Both methods are compared out of sample against the Nelson-Siegel-Svensson (NSS) model, the "
    "parametric benchmark behind several official central bank curves. KR produces smaller out-of-sample "
    "yield errors than NSS in every market: the reduction is about 13% for the United States and ranges "
    "from roughly 26% to 47% across Germany, Japan, the United Kingdom, Canada, and Switzerland.</p>"
    "<p>Under cross-validation designed to mimic real maturity gaps, KR-T reduces out-of-sample yield "
    "errors by up to a further 51% relative to standalone KR, and by 71-86% relative to NSS, while "
    "matching KR where local data are already sufficient.</p>", "accuracy"),
]) + """

    <h2>United States</h2>
""" + "\n".join([
 qa("How is the risk-free return calculated?",
    "<p>One-day rates are taken from the estimated discount curve. The one-business-day risk-free return "
    "at <em>t</em> is calculated by compounding the one-day risk-free return at <em>t</em> over the number "
    "of days between consecutive business days.</p>", "risk-free"),
 qa("How do these curves differ from the U.S. Treasury par yield curve?",
    "<p>The U.S. Department of the Treasury publishes a par yield curve based on semiannual coupon "
    "securities. This database provides daily zero-coupon yield curve rates across the complete maturity "
    "spectrum, which the Treasury does not create or publish.</p>", "vs-par-yield"),
 qa("What data products are available only for the United States?",
    "<p>Discount bond returns, term structure factors, and bond market condition measures.</p>", "us-only"),
]) + """

    <h2>International</h2>
""" + "\n".join([
 qa("Why is there no KR-T file for the United States?",
    "<p>The United States serves as the reference market in KR-T rather than a target market. KR-T files "
    "are provided for Germany, Japan, the United Kingdom, Canada, and Switzerland.</p>", "no-us-krt"),
 qa("Why can KR-T extend beyond the longest locally observed bond?",
    "<p>KR-T uses FX-hedged U.S. Treasuries as synthetic bonds, which can support maturities beyond "
    "the longest observed domestic bond. On each date, KR-T yields are published up to the last "
    "maturity supported by an observed domestic bond or a synthetic bond priced using FX forwards "
    "within the observed FX forward range.</p>", "krt-beyond-bonds"),
 qa("What is the difference between the observed maturity range and curve coverage?",
    "<p><code>min_observed_ttm</code> to <code>max_observed_ttm</code> describes the maturity range of "
    "domestic bonds used in estimation on that date. Curve coverage is the range of maturities with "
    "reported yields on that date; its upper endpoint is <code>max_curve_ttm</code>. For international "
    "KR, the upper endpoint is the longest "
    "observed domestic bond, <code>max_observed_ttm</code>. For KR-T it is the longest observed "
    "domestic bond, or an FX-transformed U.S. Treasury where one reaches further.</p>",
    "observed-vs-curve"),
 qa("Why can KR-T have a shorter date range than standalone KR?",
    "<p>KR-T additionally requires the U.S. reference market and foreign-exchange data, so its sample can "
    "begin later or contain fewer dates.</p>"
    "<p>We additionally omit 23 dates (0.06% of the KR-T sample) because of insufficient FX coverage or "
    "quote inconsistencies.</p>"
    "<details class=\"fields\"><summary>FX exclusion criteria</summary><div class=\"body\">"
    "<ul class=\"bullets\">"
    "<li>Where no domestic bond matures within one year, we require an observed FX forward of at least "
    "three months but less than one year, and we omit dates where adjacent forward tenors of three "
    "months or longer differ by more than 20 percentage points in their annualized FX-implied "
    "differentials.</li>"
    "<li>Two additional dates are excluded for isolated FX quote anomalies.</li>"
    "</ul>"
    "<p>All exclusions are based on the observed FX inputs, not on the fitted curve.</p>"
    "</div></details>", "krt-date-range"),
])
pages["faq.html"] = ("FAQ | Discount Bond Database", faq)

# --------------------------------------------------------------------------- write
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)
for fn, (title, body) in pages.items():
    with open(os.path.join(OUT_DIR, fn), "w", encoding="utf-8") as f:
        f.write(shell(fn, title, body))
print("built:", len(pages), "pages ->", OUT_DIR)
