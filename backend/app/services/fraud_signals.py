"""Nirnaya — Fraud Signal Extraction Engine.

This module extracts structured, measurable fraud signals from text.
No ML required — pure deterministic pattern matching.
Each signal is independently testable.
"""

import re
from typing import List, Tuple
from app.schemas import FraudSignals, ExtractedEntities


# ─── Pattern Libraries ──────────────────────────────────────

URGENCY_PATTERNS = [
    r"immediate(?:ly)?",
    r"urgent(?:ly)?",
    r"within \d+ (?:hour|minute|hr|min)",
    r"(?:will be|shall be|is being) (?:blocked|suspended|deactivated|terminated|closed|frozen)",
    r"last (?:chance|warning|notice|reminder)",
    r"act (?:now|immediately|fast)",
    r"(?:hurry|rush|asap|don\'?t delay)",
    r"expir(?:e|es|ing|ed) (?:today|soon|shortly|tonight|in \d+)",
    r"(?:before|by) (?:today|tonight|midnight|\d+ (?:pm|am))",
    r"time(?:\s*-?\s*)sensitive",
    r"limited (?:time|period|offer)",
]

THREAT_PATTERNS = [
    r"(?:account|a/c|acc) (?:will be|shall be|is being|has been) (?:blocked|suspended|closed|frozen|deactivated|terminated)",
    r"legal (?:action|proceedings|notice)",
    r"(?:police|fir|complaint|arrest|warrant)",
    r"penalty|fine of|penali[sz]e",
    r"(?:lose|loss of) (?:access|money|funds|account)",
    r"(?:unauthorized|suspicious) (?:activity|transaction|access|login)",
    r"fail(?:ure|ed)? to (?:comply|verify|update|respond)",
]

AUTHORITY_PATTERNS = [
    r"(?:reserve bank|rbi|sebi|irda|npci|government|ministry|uidai|income tax|it department)",
    r"(?:sbi|hdfc|icici|axis|kotak|pnb|bob|canara|union bank|indian bank)",
    r"(?:customer care|customer service|helpdesk|help desk|support team)",
    r"(?:dear (?:customer|user|valued|sir|madam|account holder))",
    r"(?:official|authorized|verified|certified) (?:notice|notification|message|communication)",
]

KYC_PATTERNS = [
    r"kyc",
    r"know your customer",
    r"pan (?:card|number|verification|update)",
    r"aadhaar (?:link|update|verify|number)",
    r"identity (?:verification|proof|update)",
    r"document (?:verification|upload|submission|update)",
    r"verify (?:your|ur) (?:identity|account|details)",
]

OTP_PATTERNS = [
    r"(?:share|send|provide|enter|give) (?:your |ur )?(?:otp|one[- ]time[- ]password|pin|cvv|password)",
    r"otp (?:is|:) ?\d{4,8}",
    r"verification code",
]

CREDENTIAL_PATTERNS = [
    r"(?:share|send|provide|enter|give|submit|verify) (?:your |ur )?(?:password|pin|cvv|card number|account number|bank details|login|credentials|net ?banking)",
    r"(?:user\s*(?:name|id)|login\s*id|customer\s*id)",
    r"(?:debit|credit|atm) card (?:number|detail|info)",
]

PAYMENT_PATTERNS = [
    r"(?:send|transfer|pay|deposit|remit) (?:rs\.?|₹|inr)?\s*\d+",
    r"processing fee",
    r"(?:registration|activation|verification|service|advance) (?:fee|charge|amount)",
    r"pay (?:to|via|through|using)",
    r"(?:refund(?:able)?|cashback|reward|prize|lottery|won|winner|claim your)",
]

REWARD_PATTERNS = [
    r"(?:congratulation|congrats)",
    r"(?:won|winner|lucky|selected|chosen)",
    r"(?:prize|reward|cashback|bonus|gift|offer)",
    r"(?:lottery|jackpot|lucky draw|bumper)",
    r"claim (?:your|the|this)",
    r"(?:free|complimentary) (?:gift|reward|offer)",
]

REFUND_PATTERNS = [
    r"refund",
    r"(?:amount|money|payment) (?:will be|has been|is being) (?:credit|refund|return|sent back)",
    r"(?:excess|extra|double|wrong) (?:payment|charge|debit|deduction)",
    r"(?:initiate|process|approve|claim) (?:your |the )?refund",
]

REMOTE_ACCESS_PATTERNS = [
    r"(?:anydesk|teamviewer|quick support|airdroid|screencast)",
    r"(?:remote|screen) (?:access|sharing|control|view)",
    r"(?:install|download) (?:this |the )?(?:app|application|software)",
]

# URL / entity patterns
URL_PATTERN = re.compile(
    r"https?://[^\s<>\"\']+|www\.[^\s<>\"\']+|[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s<>\"\']*)?",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?:\+91[\s-]?)?(?:\d[\s-]?){10}|(?:\d{5}[\s-]?\d{5})",
)

UPI_PATTERN = re.compile(
    r"[a-zA-Z0-9._-]+@(?:upi|paytm|okaxis|okicici|okhdfcbank|ybl|ibl|apl|axl|sbi|oksbi|cnrb|barodampay|pnb|freecharge|postbank|airtel|jio|kotak|citi|indus|federal|rbl|idbi|dbs|hsbc|sc|icici|hdfcbank|axisbank|bandhan|dcb|yes|kvb|idfcfirst|aubank)",
    re.IGNORECASE,
)

SHORTENED_URL_DOMAINS = [
    "bit.ly", "goo.gl", "t.co", "tinyurl.com", "is.gd", "buff.ly",
    "ow.ly", "rebrand.ly", "bl.ink", "short.io", "cutt.ly", "rb.gy",
]

LEGITIMATE_DOMAINS = {
    "sbi": ["sbi.co.in", "onlinesbi.sbi", "bank.sbi"],
    "hdfc": ["hdfcbank.com", "hdfcbank.net"],
    "icici": ["icicibank.com"],
    "axis": ["axisbank.com"],
    "kotak": ["kotak.com", "kotak811.com"],
    "pnb": ["pnbindia.in"],
    "bob": ["bankofbaroda.in"],
    "canara": ["canarabank.com"],
    "rbi": ["rbi.org.in"],
    "npci": ["npci.org.in"],
    "paytm": ["paytm.com"],
    "phonepe": ["phonepe.com"],
    "googlepay": ["pay.google.com"],
}


def _matches_any(text: str, patterns: list) -> bool:
    """Check if text matches any pattern in the list."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def _extract_amounts(text: str) -> List[float]:
    """Extract monetary amounts from text."""
    amount_pattern = re.compile(
        r"(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d{1,2})?)|"
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:rs\.?|₹|rupee)",
        re.IGNORECASE,
    )
    amounts = []
    for match in amount_pattern.finditer(text):
        raw = match.group(1) or match.group(2)
        if raw:
            try:
                amounts.append(float(raw.replace(",", "")))
            except ValueError:
                pass
    return amounts


def _detect_claimed_org(text: str) -> str | None:
    """Detect which organization the message claims to be from."""
    text_lower = text.lower()
    for org in LEGITIMATE_DOMAINS:
        if org in text_lower:
            return org.upper()
    # Check for common authority claims
    if re.search(r"\brbi\b", text_lower):
        return "RBI"
    if re.search(r"\bsebi\b", text_lower):
        return "SEBI"
    if re.search(r"\bnpci\b", text_lower):
        return "NPCI"
    return None


def _check_domain_mismatch(urls: List[str], claimed_org: str | None) -> bool:
    """Check if extracted URLs match the claimed organization's legitimate domains."""
    if not claimed_org or not urls:
        return False
    org_key = claimed_org.lower()
    legit_domains = LEGITIMATE_DOMAINS.get(org_key, [])
    if not legit_domains:
        return False
    for url in urls:
        # Extract domain from URL
        domain_match = re.search(r"(?:https?://)?(?:www\.)?([^/\s:]+)", url.lower())
        if domain_match:
            domain = domain_match.group(1)
            if not any(domain.endswith(ld) for ld in legit_domains):
                return True
    return False


def _check_shortened_url(urls: List[str]) -> bool:
    """Check if any URL uses a URL shortener."""
    for url in urls:
        for short_domain in SHORTENED_URL_DOMAINS:
            if short_domain in url.lower():
                return True
    return False


def extract_entities(text: str) -> ExtractedEntities:
    """Extract structured entities from text."""
    urls = URL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    upis = UPI_PATTERN.findall(text)
    amounts = _extract_amounts(text)
    claimed_org = _detect_claimed_org(text)

    # Determine action requested
    action = None
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["kyc", "verify", "update"]):
        action = "KYC/verification"
    elif any(kw in text_lower for kw in ["pay", "send", "transfer"]):
        action = "payment"
    elif any(kw in text_lower for kw in ["claim", "collect", "redeem"]):
        action = "claim reward"
    elif any(kw in text_lower for kw in ["install", "download"]):
        action = "install software"
    elif any(kw in text_lower for kw in ["call", "contact"]):
        action = "contact"

    return ExtractedEntities(
        claimed_organization=claimed_org,
        urls=urls,
        phones=phones,
        upis=upis,
        amounts=amounts,
        action_requested=action,
    )


def extract_fraud_signals(text: str, entities: ExtractedEntities) -> FraudSignals:
    """Extract all fraud signals from text and entities."""
    return FraudSignals(
        urgency=_matches_any(text, URGENCY_PATTERNS),
        threat_language=_matches_any(text, THREAT_PATTERNS),
        authority_impersonation=_matches_any(text, AUTHORITY_PATTERNS),
        kyc_request=_matches_any(text, KYC_PATTERNS),
        otp_request=_matches_any(text, OTP_PATTERNS),
        credential_request=_matches_any(text, CREDENTIAL_PATTERNS),
        payment_request=_matches_any(text, PAYMENT_PATTERNS),
        url_present=len(entities.urls) > 0,
        phone_present=len(entities.phones) > 0,
        upi_present=len(entities.upis) > 0,
        suspicious_domain=any(
            not any(url.lower().endswith(ld) for ld in sum(LEGITIMATE_DOMAINS.values(), []))
            for url in entities.urls
        ) if entities.urls else False,
        domain_mismatch=_check_domain_mismatch(entities.urls, entities.claimed_organization),
        reward_language=_matches_any(text, REWARD_PATTERNS),
        refund_language=_matches_any(text, REFUND_PATTERNS),
        remote_access_request=_matches_any(text, REMOTE_ACCESS_PATTERNS),
        shortened_url=_check_shortened_url(entities.urls),
    )
