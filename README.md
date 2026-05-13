<div align="center">

```
██╗   ██╗ ██████╗ ██╗  ████████╗
██║   ██║██╔═══██╗██║     ██║   
██║   ██║██║   ██║██║     ██║   
╚██╗ ██╔╝██║   ██║██║     ██║   
 ╚████╔╝ ╚██████╔╝███████╗██║   
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝   
```

**Web Authentication Assessment Engine · v6.0**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Santonu%20Halder-orange?style=flat-square&logo=github)](https://github.com/santonuhalder)
[![Threads](https://img.shields.io/badge/Threads-100%20Concurrent-red?style=flat-square)](volt_v6.py)
[![Payloads](https://img.shields.io/badge/SQLi%20Payloads-143-purple?style=flat-square)](volt_v6.py)

> ⚠️ **For authorised penetration testing and security research only.**
> Unauthorised use against systems you do not own or have explicit written permission to test is illegal.

</div>

---

## ◆ Overview

**VOLT** is a high-performance, multi-threaded web authentication assessment framework. It automatically detects the target stack — **WordPress** or generic web login — and deploys the appropriate attack vector: XML-RPC multicall brute-force, wp-login.php credential stuffing, or a comprehensive 143-payload SQL injection bypass suite with WAF evasion.

Every confirmed hit is verified for **administrator + plugin-install capability** before being saved — zero false positives in the output.

---

## ◆ Feature Matrix

| Capability | Detail |
|---|---|
| **Concurrency** | 100 independent threads, each with its own session |
| **WordPress Detection** | Signature scan + path probing (`wp-content`, `wp-includes`, `xmlrpc.php`) |
| **XML-RPC Brute** | `system.multicall` batched (8 creds/call) → `isAdmin` flag verification |
| **wp-login.php Brute** | 302-redirect + cookie detection, UserPro plugin fallback |
| **Admin Verification** | `wp.getUsersBlogs` → `isAdmin==1` + `wp.getCapabilities` → `install_plugins==1` |
| **Plugin-Install Check** | `/wp-admin/` → `plugin-install.php` link · `/wp-admin/plugins.php` · REST API |
| **SQLi Engine** | 143 payloads: Classic OR · UNION · Blind · MSSQL · Oracle · PostgreSQL · SQLite |
| **WAF Evasion** | URL encoding · comment obfuscation · case mutation · whitespace · hex/concat |
| **CSRF Handling** | Auto-refreshes hidden tokens before every injection attempt |
| **Login Discovery** | 80+ static paths + homepage spider + meta-refresh / JS redirect parsing |
| **Form Parser** | Multi-strategy: name/id/autocomplete/placeholder/label → field identification |
| **Output** | `Valid.txt` (SQLi) · `WP_Successful.txt` (WP admin+plugins confirmed) |

---

## ◆ Attack Flow

```
Input: domains.txt
       │
       ▼
   [Dead Check]  ──────────────────────────────────► skip
       │
       ▼
   [WordPress?]
       │
   YES ▼                          NO ▼
[XML-RPC alive?]           [Find Login Form]
       │                          │
   YES ▼            NO ▼    found ▼         not found ▼
[Multicall Brute] [wp-login  [SQLi 143       skip
       │           Brute]     Payloads]
       │             │             │
       └─────────────┘             │
              ▼                    ▼
    [Verify: isAdmin +         [Score-based
     install_plugins]          detection]
              │                    │
           PASS ▼               PASS ▼
     WP_Successful.txt        Valid.txt
```

---

## ◆ SQLi Detection Engine

VOLT uses a **multi-signal scoring system** — not a single keyword match — to eliminate false positives:

| Signal | Points |
|---|---|
| URL navigated to known admin path (`/wp-admin`, `/dashboard`, etc.) | +2 |
| Navigated away from login with no error in URL | +1 |
| New authentication cookie appeared in response | +2 |
| Admin-specific body keywords present (off login page) | +1 |
| Admin path accessible with current session | +2 |

**Threshold: ≥ 2 points** → confirmed bypass. Hard-fail patterns (error messages, fail signatures) immediately discard the result.

---

## ◆ Installation

```bash
git clone https://github.com/santonuhalder/volt
cd volt
pip install -r requirements.txt
```

**Requirements:** Python 3.8+

---

## ◆ Usage

```bash
python3 volt_v6.py
```

```
Enter Your File Name: domains.txt
```

**Input format** (`domains.txt`) — one target per line:
```
example.com
https://target.org
http://site.net
192.168.1.100
```

Bare domains (no scheme) are auto-prefixed with `https://`. Lines starting with `#` are ignored.

---

## ◆ Output Files

| File | Contents |
|---|---|
| `Valid.txt` | `login_url  \|  "username"  \|  "payload"` — confirmed SQLi bypasses |
| `WP_Successful.txt` | `host/wp-login.php#user@pass` — confirmed WP admin with plugin-install |

Both files are created on first run with a timestamped header. Results are appended in real-time, thread-safe.

---

## ◆ Configuration

Edit the constants at the top of `volt_v6.py`:

```python
THREADS         = 100   # concurrent workers
TIMEOUT_CONNECT = 6     # seconds
TIMEOUT_READ    = 15    # seconds
MAX_RETRIES     = 1     # per request
```

---

## ◆ WordPress Credential List

VOLT ships with **70 default WP credential pairs** covering the most common admin defaults:

```
admin:admin  ·  admin:password  ·  admin:123456  ·  admin:wordpress
administrator:admin  ·  root:root  ·  webmaster:admin  ·  ...
```

To use a custom wordlist, replace the `WP_CREDS` list in the source.

---

## ◆ Terminal Output

```
  [◆]  target.com                                         ->  [WordPress - Detected]
  [⡿]  target.com                                         ->  [WordPress - XML-RPC Alive]
  [▶]  target.com                                         ->  [WordPress - XML-RPC Brute]
  [✔]  target.com                                         ->  [Admin+Plugins Confirmed  |  admin  :  password123  [XML-RPC]]

  [◆]  site.org                                           ->  [Form Found - SQLi Injecting]
  [✔]  site.org                                           ->  [SQLi Successful  |  ' OR '1'='1'--  :  x]

  [○]  dead.example.com                                   ->  [Dead]
```

---

## ◆ Disclaimer

```
This tool is provided for educational purposes and authorised security testing only.
The author assumes no liability for any misuse or damage caused by this software.
You are solely responsible for ensuring you have explicit written permission
from the system owner before running any tests.
```

---

## ◆ Author

<div align="center">

| | |
|---|---|
| **Name** | Santonu Halder |
| **GitHub** | [github.com/santonuhalder](https://github.com/santonuhalder) |
| **License** | MIT |

</div>

---

<div align="center">
<sub>VOLT v6.0 · Web Authentication Assessment Engine · Built for security professionals</sub>
</div>
