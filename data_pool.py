import hashlib
import json
import os
import re
from typing import Any, Dict, List, Tuple

POOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "open_data_pool.json")

PII_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    ("id_card", re.compile(r"(?<!\d)(?:\d{17}[\dXx]|\d{15})(?!\d)"), "[身份证号已脱敏]"),
    ("phone", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[手机号已脱敏]"),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[邮箱已脱敏]"),
    ("bank_card", re.compile(r"(?<!\d)\d{16,19}(?!\d)"), "[银行卡号已脱敏]"),
    ("api_key", re.compile(r"\b(?:sk|pk)-[A-Za-z0-9_-]{16,}\b", re.I), "[密钥已脱敏]"),
]


def load_pool() -> List[Dict[str, Any]]:
    try:
        with open(POOL_FILE, "r", encoding="utf-8") as f:
            rows = json.load(f)
        return rows if isinstance(rows, list) else []
    except (OSError, ValueError, TypeError):
        return []


def mask_text(text: str) -> Tuple[str, List[str]]:
    value = str(text or "")
    detected: List[str] = []
    for name, pattern, replacement in PII_PATTERNS:
        value, count = pattern.subn(replacement, value)
        if count:
            detected.append(name)
    return value, detected


def pseudonymize(value: str, prefix: str = "匿名对象") -> str:
    digest = hashlib.sha256(("maesi-open-demo:" + str(value)).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def search_pool(terms: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for row in load_pool():
        text = (str(row.get("title", "")) + " " + str(row.get("content", ""))).lower()
        matched = [term for term in terms if term.lower() in text]
        if not matched:
            continue
        item = dict(row)
        item["_matched"] = matched
        item["_score"] = len(matched) / max(1, min(len(terms), 8))
        item["_source"] = "open_data_pool"
        scored.append(item)
    scored.sort(key=lambda x: (x["_score"], len(x["_matched"])), reverse=True)
    return scored[:top_k]
