"""Intent detection for emails."""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib

_ALLOWED_LABELS = {"PRAISE", "RESUME", "COMPLAINT", "SUPPORT", "OTHER"}
_DEFAULT_MODEL_PATH = Path("models") / "intent_classifier.joblib"

_PRIORITY = ["COMPLAINT", "SUPPORT", "RESUME", "PRAISE", "OTHER"]


@dataclass(frozen=True)
class IntentPrediction:
    """Intent prediction result."""
    label: str
    confidence: float
    source: str
    secondary: tuple[str, ...] = ()
    reason: str = ""


def detect_intent(text: str, min_confidence: float = 0.60) -> IntentPrediction:
    """Detect intent using ML with safe rule fallback."""
    rules_pred = detect_intent_rules(text)
    ml_pred = _detect_intent_ml(text)

    if ml_pred is None:
        return rules_pred

    if ml_pred.confidence < min_confidence:
        return rules_pred

    if ml_pred.label == "RESUME" and not _looks_like_resume(text):
        return rules_pred

    merged_secondary = _merge_secondary(primary=ml_pred.label, rules=rules_pred)
    reason = _merge_reason(primary_source="local_ml", ml=ml_pred, rules=rules_pred)

    return IntentPrediction(
        label=ml_pred.label,
        confidence=ml_pred.confidence,
        source="local_ml",
        secondary=merged_secondary,
        reason=reason,
    )


def detect_intent_rules(text: str) -> IntentPrediction:
    """Detect intent using regex rules with multi-label support."""
    value = _normalize(text)
    matches = _collect_rule_matches(value)

    if not matches:
        return IntentPrediction(label="OTHER", confidence=0.50, source="rules")

    primary = _pick_primary(matches)
    secondary = tuple(sorted(i for i in matches if i != primary))
    reason = _build_rules_reason(matches=matches, primary=primary)

    return IntentPrediction(
        label=primary,
        confidence=0.95,
        source="rules",
        secondary=secondary,
        reason=reason,
    )


def normalize_category(category: str, intent: str) -> str:
    """Normalize productive category using intent overrides."""
    if intent in {"SUPPORT", "COMPLAINT", "RESUME"}:
        return "Produtivo"
    if intent in {"PRAISE"}:
        return "Improdutivo"
    return category


def _detect_intent_ml(text: str) -> IntentPrediction | None:
    """Detect intent using the local ML model when available."""
    model = _load_intent_model(str(_DEFAULT_MODEL_PATH))
    if model is None:
        return None

    pipeline, classes = _unwrap_model(model)
    label, confidence = _predict_label_and_confidence(pipeline, classes, text)

    label = label if label in _ALLOWED_LABELS else "OTHER"
    return IntentPrediction(label=label, confidence=_clamp(confidence), source="local_ml")


@lru_cache(maxsize=4)
def _load_intent_model(path: str) -> Any | None:
    """Load and cache the intent model bundle."""
    model_path = Path(path)
    if not model_path.exists():
        return None
    try:
        return joblib.load(model_path)
    except Exception:
        return None


def _unwrap_model(model: Any) -> tuple[Any, list[str] | None]:
    """Unwrap bundle formats into (pipeline, classes)."""
    if isinstance(model, dict) and "pipeline" in model:
        pipeline = model["pipeline"]
        labels = model.get("labels")
        if isinstance(labels, list) and labels:
            return pipeline, [str(x) for x in labels]
        return pipeline, None
    return model, None


def _predict_label_and_confidence(
    pipeline: Any,
    classes: list[str] | None,
    text: str,
) -> tuple[str, float]:
    """Predict label and confidence from a probabilistic classifier."""
    predict_proba = getattr(pipeline, "predict_proba", None)
    if not callable(predict_proba):
        return "OTHER", 0.50

    proba_row = predict_proba([text])[0]
    proba = [float(x) for x in proba_row]

    resolved_classes = classes or _resolve_classes_from_pipeline(pipeline)
    if not resolved_classes or len(resolved_classes) != len(proba):
        return "OTHER", max(proba) if proba else 0.50

    best_idx = int(max(range(len(proba)), key=lambda i: proba[i]))
    return str(resolved_classes[best_idx]), float(proba[best_idx])


def _resolve_classes_from_pipeline(pipeline: Any) -> list[str] | None:
    """Resolve classes_ from pipeline or its final estimator."""
    direct = getattr(pipeline, "classes_", None)
    if isinstance(direct, (list, tuple)) and direct:
        return [str(x) for x in direct]

    named_steps = getattr(pipeline, "named_steps", None)
    if isinstance(named_steps, dict):
        clf = named_steps.get("clf")
        clf_classes = getattr(clf, "classes_", None)
        if isinstance(clf_classes, (list, tuple)) and clf_classes:
            return [str(x) for x in clf_classes]

    return None


def _looks_like_resume(text: str) -> bool:
    """Check if text contains resume-related keywords."""
    value = _normalize(text)
    return _matches(value, _RESUME_PATTERNS)


def _normalize(text: str) -> str:
    """Normalize text for pattern matching."""
    value = (text or "").lower()
    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _matches(value: str, patterns: list[str]) -> bool:
    """Check if any regex pattern matches."""
    return any(re.search(p, value) for p in patterns)


def _clamp(value: float) -> float:
    """Clamp numeric value to 0..1."""
    return max(0.0, min(1.0, float(value)))


def _collect_rule_matches(value: str) -> set[str]:
    """Collect all rule-based intent matches."""
    matches: set[str] = set()

    if _matches(value, _PRAISE_PATTERNS):
        matches.add("PRAISE")
    if _matches(value, _RESUME_PATTERNS):
        matches.add("RESUME")
    if _matches(value, _COMPLAINT_PATTERNS):
        matches.add("COMPLAINT")
    if _matches(value, _SUPPORT_PATTERNS):
        matches.add("SUPPORT")

    matches = {m for m in matches if m in _ALLOWED_LABELS}
    return matches


def _pick_primary(matches: set[str]) -> str:
    """Pick a primary intent using priority order."""
    for label in _PRIORITY:
        if label in matches:
            return label
    return "OTHER"


def _build_rules_reason(matches: set[str], primary: str) -> str:
    """Build a short explanation for rule matches."""
    ordered = [m for m in _PRIORITY if m in matches]
    secondary = [m for m in ordered if m != primary]
    if not secondary:
        return f"rules: matched {primary}"
    return f"rules: matched {primary}; secondary={','.join(secondary)}"


def _merge_secondary(primary: str, rules: IntentPrediction) -> tuple[str, ...]:
    """Merge rules-based intents as secondary labels."""
    primary_norm = (primary or "OTHER").strip().upper()
    all_rules = {rules.label, *rules.secondary}
    cleaned = sorted(i for i in all_rules if i in _ALLOWED_LABELS and i != primary_norm)
    return tuple(cleaned)


def _merge_reason(primary_source: str, ml: IntentPrediction, rules: IntentPrediction) -> str:
    """Merge reason strings from ML and rules."""
    rules_part = rules.reason or f"rules: matched {rules.label}"
    ml_part = f"local_ml: {ml.label} conf={ml.confidence:.2f}"
    return f"{ml_part}; {rules_part}; chosen={primary_source}"


_PRAISE_PATTERNS = [
    r"\belogio\b",
    r"\bparab[eé]ns\b",
    r"\bótimo\b",
    r"\bexcelente\b",
    r"\bmuito bom\b",
    r"\btop\b",
    r"\bperfeito\b",
    r"\bmaravilhos[oa]\b",
    r"\bimpec[aá]vel\b",
    r"\bsensacional\b",
    r"\badorei\b",
    r"\bamei\b",
    r"\bgostei\b",
    r"\bagrade[cç]o\b",
    r"\bagradecimento\b",
    r"\bobrigad[oa]\b",
    r"\bboa funcionalidade\b",
    r"\bbom atendimento\b",
    r"\bme ajudou\b",
    r"\bresolveram\b",
    r"\brecomendo\b",
]

_RESUME_PATTERNS = [
    r"\bcurr[ií]culo\b",
    r"\bcurriculo\b",
    r"\bcv\b",
    r"\bvaga\b",
    r"\bvaga(s)?\b",
    r"\boportunidade\b",
    r"\btrabalhe conosco\b",
    r"\bprocesso seletivo\b",
    r"\bseletivo\b",
    r"\bentrevista\b",
    r"\brecrutamento\b",
    r"\brh\b",
    r"\brecursos humanos\b",
    r"\bcandidatura\b",
    r"\bcandidato\b",
    r"\baplica[cç][aã]o\b",
    r"\bapply\b",
    r"\bjob\b",
    r"\bposition\b",
    r"\bcover letter\b",
    r"\bcarta de apresenta[cç][aã]o\b",
    r"\bportf[oó]lio\b",
    r"\blinkedin\b",
    r"\bgithub\b",
    r"\banexo\b.*\bcv\b",
    r"\banexo\b.*\bcurr[ií]culo\b",
]

_COMPLAINT_PATTERNS = [
    r"\breclama[cç][aã]o\b",
    r"\bdecepcionad[oa]\b",
    r"\binsatisfeit[oa]\b",
    r"\binsatisfa[cç][aã]o\b",
    r"\bfrustra(?:do|da|ç[aã]o)\b",
    r"\bp[eé]ssimo\b",
    r"\bhorr[ií]vel\b",
    r"\bproblema\b",
    r"\berro\b",
    r"\bfalha\b",
    r"\bn[aã]o funciona\b",
    r"\bn[aã]o est[aá] funcionando\b",
    r"\bexperi[eê]ncia ruim\b",
    r"\bservi[cç]o ruim\b",
    r"\bquero cancelar\b",
    r"\bcancel(?:ar|amento)\b",
    r"\bquero reembolso\b",
    r"\breembolso\b",
    r"\bestorno\b",
    r"\bdevolu[cç][aã]o\b",
    r"\bcobran[cç]a indevida\b",
    r"\bme cobraram\b",
    r"\bcobrado\b",
    r"\bpagamento duplicado\b",
    r"\bn[aã]o (?:estou|fiquei|ficamos) satisfeit[oa]\b",
    r"\bn[aã]o gostei\b",
    r"\bquero meu dinheiro de volta\b",
]

_SUPPORT_PATTERNS = [
    r"\bsuporte\b",
    r"\bajuda\b",
    r"\bpreciso de ajuda\b",
    r"\bme ajuda\b",
    r"\bd[uú]vida\b",
    r"\bcomo (?:fa[cç]o|fazer)\b",
    r"\bcomo (?:usar|configurar)\b",
    r"\berro\b",
    r"\bbug\b",
    r"\bfalha\b",
    r"\bn[aã]o consigo\b",
    r"\bn[aã]o consigo acessar\b",
    r"\bn[aã]o consigo entrar\b",
    r"\blogin\b",
    r"\bsenha\b",
    r"\breseta(?:r|r senha)\b",
    r"\bredefinir senha\b",
    r"\bchamado\b",
    r"\bticket\b",
    r"\bstatus\b",
    r"\bpendente\b",
    r"\bapi\b",
    r"\btoken\b",
    r"\bauth\b",
]
