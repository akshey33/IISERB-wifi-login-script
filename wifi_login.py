import requests
import re
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(InsecureRequestWarning)

# ==========================
# YOUR CREDENTIALS
# ==========================

USERNAME = input("Username: ")
PASSWORD = input("Password: ")

# ==========================
# SESSION
# ==========================

s = requests.Session()

# ==========================
# CHECK IF INTERNET ALREADY WORKS
# ==========================

try:
    r = s.get(
        "https://www.google.com/generate_204",
        timeout=5
    )

    if r.status_code == 204:
        print("Already authenticated.")
        raise SystemExit

except Exception:
    pass

# ==========================
# TRIGGER CAPTIVE PORTAL
# ==========================

try:
    r = s.get(
        "http://neverssl.com",
        timeout=10
    )

except Exception as e:
    print("Could not reach captive portal:")
    print(e)
    raise SystemExit

# ==========================
# EXTRACT FORTIGATE REDIRECT
# ==========================

m = re.search(
    r'window\.location="([^"]+)"',
    r.text
)

if not m:
    print("No captive portal detected.")
    raise SystemExit

portal_url = m.group(1)

print("Portal URL:")
print(portal_url)

# ==========================
# OPEN LOGIN PAGE
# ==========================

login_page = s.get(
    portal_url,
    verify=False,
    timeout=10
)

html = login_page.text

# ==========================
# EXTRACT HIDDEN FIELDS
# ==========================

magic = re.search(
    r'name="magic"\s+value="([^"]+)"',
    html
)

redir = re.search(
    r'name="4Tredir"\s+value="([^"]+)"',
    html
)

if not magic or not redir:
    print("Could not find login form.")
    raise SystemExit

magic = magic.group(1)
redir = redir.group(1)

print("magic =", magic)
print("redir =", redir)

# ==========================
# LOGIN
# ==========================

payload = {
    "4Tredir": redir,
    "magic": magic,
    "username": USERNAME,
    "password": PASSWORD,
}

resp = s.post(
    "https://gateway.iiserb.ac.in:1003/",
    data=payload,
    verify=False,
    allow_redirects=True,
    timeout=10
)

print("\nLogin response URL:")
print(resp.url)

# ==========================
# VERIFY LOGIN
# ==========================

try:
    test = s.get(
        "https://www.google.com/generate_204",
        timeout=10
    )

    if test.status_code == 204:
        print("\nLOGIN SUCCESSFUL")
    else:
        print("\nLOGIN MAY HAVE FAILED")

except Exception:
    print("\nLOGIN VERIFICATION FAILED")
