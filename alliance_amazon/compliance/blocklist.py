from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BlockedTerm:
    rule_id: str
    severity: str  # "hard" | "soft"
    category: str
    term: str


def iter_blocked_terms() -> Iterable[BlockedTerm]:
    # Derived from alliance-amazon-seo-master-plan (3).md (Jan 2024).
    hard_antimicrobial = [
        "disinfect",
        "disinfectant",
        "disinfecting",
        "sanitize",
        "sanitizer",
        "sanitizing",
        "antimicrobial",
        "antibacterial",
        "antifungal",
        "antiviral",
        "anti-mold",
        "anti-mildew",
        "germicidal",
        "germicide",
        "bactericidal",
        "bactericide",
        "fungicidal",
        "fungicide",
        "virucidal",
        "virucide",
        "sterilize",
        "sterilizing",
        "sterilant",
        "kills germs",
        "kills bacteria",
        "kills viruses",
        "kills mold",
        "kills fungus",
        "destroys germs",
        "destroys bacteria",
        "eliminates germs",
        "eliminates bacteria",
        "removes germs",
        "removes bacteria",
        "prevents bacterial growth",
        "prevents mold growth",
        "prevents mildew",
        "stops bacteria",
        "germ-free",
        "bacteria-free",
        "virus-free",
        "99.9% of germs",
        "hospital-grade",
        "medical-grade disinfection",
    ]
    hard_pesticide = [
        "repels insects",
        "insect repellent",
        "repels bugs",
        "bug repellent",
        "repels mosquitoes",
        "mosquito repellent",
        "repels rodents",
        "rodent repellent",
        "kills insects",
        "insecticide",
        "kills ants",
        "kills roaches",
        "kills spiders",
        "pest control",
        "pest killer",
        "keeps bugs away",
        "deters pests",
    ]
    hard_medical = [
        "relieves pain",
        "reduces inflammation",
        "treats infection",
        "medical grade",
        "pharmaceutical grade",
        "fda approved",
    ]
    hard_health = [
        "removes allergens",
        "eliminates allergens",
        "hypoallergenic",
        "allergy-free",
        "asthma-safe",
        "improves air quality",
        "purifies air",
        "detoxifies",
        "detoxifying",
        "cleanses toxins",
    ]
    hard_safety = [
        "non-toxic",
        "nontoxic",
        "chemical-free",
        "toxin-free",
        "completely safe",
        "100% safe",
        "totally safe",
        "absolutely safe",
        "perfectly safe",
        "harmless",
        "no harmful chemicals",
        "safe for everyone",
        "safe for all uses",
        "child-safe",
        "pet-safe",
    ]
    soft_environment = [
        "eco-friendly",
        "environmentally friendly",
        "sustainable",
        "biodegradable",
        "compostable",
        "recyclable",
        "carbon neutral",
        "zero waste",
        "planet-friendly",
        "earth-friendly",
        "natural",
        "all-natural",
        "organic",
    ]
    soft_superiority = [
        "best",
        "#1",
        "number one",
        "leading",
        "top-rated",
        "most effective",
        "strongest",
        "most powerful",
        "better than",
        "superior to",
        "outperforms",
        "unmatched",
        "unbeatable",
    ]

    for term in hard_antimicrobial:
        yield BlockedTerm("A", "hard", "antimicrobial", term)
    for term in hard_pesticide:
        yield BlockedTerm("B", "hard", "pesticide", term)
    for term in hard_medical:
        yield BlockedTerm("C", "hard", "medical", term)
    for term in hard_health:
        yield BlockedTerm("D", "hard", "health", term)
    for term in hard_safety:
        yield BlockedTerm("E", "hard", "safety", term)
    for term in soft_environment:
        yield BlockedTerm("F", "soft", "environment", term)
    for term in soft_superiority:
        yield BlockedTerm("G", "soft", "superiority", term)
