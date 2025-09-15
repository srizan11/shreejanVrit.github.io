import re
import dns.resolver
import smtplib
import socket

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

DNS_TIMEOUT = 5.0
SMTP_TIMEOUT = 5.0

def is_valid_format(email: str) -> bool:
    return bool(EMAIL_REGEX.fullmatch(email))

def get_mx_records(domain: str):
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=DNS_TIMEOUT)
        mxs = sorted([(r.preference, str(r.exchange).rstrip(".")) for r in answers], key=lambda x: x[0])
        return mxs
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return []
    except Exception as e:
        return []

def smtp_check(mx_host: str, from_address="probe@example.com", to_address=None):
    try:
        if to_address is None:
            return {"deliverable": False, "error": "no recipient specified"}
        server = smtplib.SMTP(timeout=SMTP_TIMEOUT)
        server.connect(mx_host, 25)
        server.helo()
        server.mail(from_address)
        code, resp = server.rcpt(to_address)
        server.quit()
        return {"deliverable": code in (250, 251), "code": code, "response": resp.decode() if isinstance(resp, bytes) else resp}
    except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, socket.timeout) as e:
        return {"deliverable": False, "error": str(e)}
    except Exception as e:
        return {"deliverable": False, "error": str(e)}

def check_spf(domain: str):
    try:
        answers = dns.resolver.resolve(domain, "TXT", lifetime=DNS_TIMEOUT)
        txts = [b"".join(r.strings).decode() if hasattr(r, "strings") else str(r) for r in answers]
        spf_strs = [t for t in txts if t.lower().startswith("v=spf1")]
        if not spf_strs:
            return "none"
        return "present"
    except Exception:
        return "none"

def check_dmarc(domain: str):
    try:
        name = f"_dmarc.{domain}"
        answers = dns.resolver.resolve(name, "TXT", lifetime=DNS_TIMEOUT)
        txts = [b"".join(r.strings).decode() if hasattr(r, "strings") else str(r) for r in answers]
        dmarc_strs = [t for t in txts if t.lower().startswith("v=dmarc1")]
        if not dmarc_strs:
            return "none"
        return "present"
    except Exception:
        return "none"

def check_dkim(domain: str, selectors_to_try=None):
    if selectors_to_try is None:
        selectors_to_try = ["default", "selector1", "google"]
    for sel in selectors_to_try:
        name = f"{sel}._domainkey.{domain}"
        try:
            answers = dns.resolver.resolve(name, "TXT", lifetime=DNS_TIMEOUT)
            txts = [b"".join(r.strings).decode() if hasattr(r, "strings") else str(r) for r in answers]
            dkim_strs = [t for t in txts if "v=DKIM1" in t or "v=dkim1" in t]
            if dkim_strs:
                return "present"
        except Exception:
            continue
    return "unknown"
