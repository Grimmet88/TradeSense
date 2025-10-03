import os
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict

def utcnow():
    return datetime.now(timezone.utc)

@dataclass
class Headline:
    title: str
    summary: str
    link: str
    source: str
    published_at: datetime

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["published_at"] = self.published_at.isoformat()
        return d

def dedupe(items: List[Headline]) -> List[Headline]:
    seen = set()
    out: List[Headline] = []
    for h in items:
        key = hashlib.md5(f"{h.title}|{h.link}".encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out

def env_list(name: str, default: List[str]) -> List[str]:
    raw = os.getenv(name, "")
    if not raw:
        return default
    return [s.strip() for s in raw.split(",") if s.strip()]

