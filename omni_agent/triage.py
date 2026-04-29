"""Triage: classify task type, detect priority and missing context."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from omni_agent.scanner import ParsedTask


PATH_HINT_RE = re.compile(r"([A-Za-z0-9_./-]+\.[A-Za-z]{1,5})")
DEPENDENCY_RE = re.compile(r"\b(depends on|requires|needs)\b\s+([^.,;\n]+)", re.IGNORECASE)


@dataclass
class TriageResult:
    task_type: str
    priority: int
    persona_order: List[str]
    missing_context: List[str]
    dependencies: List[str]
    path_hints: List[str]
    confidence: float


def _classify_type(text: str, type_keywords: Dict[str, List[str]]) -> str:
    lower = text.lower()
    scores: Dict[str, int] = {t: 0 for t in type_keywords}
    for ttype, kws in type_keywords.items():
        for k in kws:
            if k.lower() in lower:
                scores[ttype] += 1
    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        return "backend"  # default per spec ordering
    return best_type


def _detect_priority(text: str, priority_keywords: Dict[int, List[str]]) -> int:
    lower = text.lower()
    for prio, kws in sorted(priority_keywords.items()):
        for k in kws:
            if k.lower() in lower:
                return int(prio)
    return 3


def _detect_path_hints(text: str) -> List[str]:
    hints: List[str] = []
    for m in PATH_HINT_RE.findall(text):
        if "/" in m or m.endswith(
            (".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".yaml", ".yml", ".json")
        ):
            hints.append(m.strip("`'\""))
    return list(dict.fromkeys(hints))


def _detect_dependencies(text: str) -> List[str]:
    deps: List[str] = []
    for m in DEPENDENCY_RE.findall(text):
        deps.append(m[1].strip())
    return deps


def _detect_missing_context(text: str, path_hints: List[str], task_type: str) -> List[str]:
    missing: List[str] = []
    lower = text.lower()
    if task_type == "backend" and not path_hints and "create" in lower:
        missing.append("explicit target file path under backend/app/**")
    if "integrate" in lower and "provider" in lower and not path_hints:
        missing.append("third-party provider name and credentials channel")
    if "tbd" in lower or "todo: tbd" in lower:
        missing.append("definition for TBD items in task text")
    return missing


def triage_task(task: ParsedTask, config: dict) -> TriageResult:
    tcfg = config.get("triage", {}) or {}
    type_keywords = tcfg.get("type_keywords", {})
    priority_keywords = {int(k): v for k, v in (tcfg.get("priority_keywords") or {}).items()}

    task_type = _classify_type(task.text, type_keywords) if type_keywords else "backend"
    priority = _detect_priority(task.text, priority_keywords) if priority_keywords else 3
    path_hints = _detect_path_hints(task.text)
    dependencies = _detect_dependencies(task.text)
    missing = _detect_missing_context(task.text, path_hints, task_type)

    persona_order = ["analyst", "developer", "evaluator"]
    confidence = 0.6 + 0.1 * min(3, len(path_hints)) - 0.1 * min(3, len(missing))
    confidence = max(0.0, min(1.0, confidence))

    return TriageResult(
        task_type=task_type,
        priority=priority,
        persona_order=persona_order,
        missing_context=missing,
        dependencies=dependencies,
        path_hints=path_hints,
        confidence=confidence,
    )
