"""Evaluator persona: validates acceptance criteria, runs tests, computes cohesion."""
from __future__ import annotations

import json
import logging
import os
import py_compile
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

from omni_agent.llm_client import LLMClient, LLMUnavailable


logger = logging.getLogger("omni_agent.evaluator")


SYSTEM_PROMPT = (
    "You are the Evaluator persona inside an Omni-Agent. "
    "Given a mini-spec, applied changes, and test results, assess each acceptance criterion. "
    "Return strict JSON: {\"criteria\": [{\"text\": \"...\", \"met\": true|false, \"evidence\": \"...\"}], "
    "\"regression_ok\": true|false, \"summary\": \"...\"}. JSON only."
)


def _check_file_exists_and_compiles(repo_root: Path, rel_path: str) -> Tuple[bool, str]:
    full = repo_root / rel_path
    if not full.exists():
        return False, f"file missing: {rel_path}"
    if full.suffix == ".py":
        try:
            py_compile.compile(str(full), doraise=True)
            return True, f"py_compile ok: {rel_path}"
        except py_compile.PyCompileError as e:
            return False, f"py_compile failed: {e}"
    return True, f"file present: {rel_path}"


def _run_pytest(repo_root: Path, target: str = "backend/tests") -> Dict[str, Any]:
    target_path = repo_root / target
    if not target_path.exists() or not any(target_path.rglob("test_*.py")):
        return {"ran": False, "exit_code": None, "status": "skipped", "output": "no tests found"}
    cmd = ["python", "-m", "pytest", "-q", str(target_path)]
    try:
        res = subprocess.run(
            cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=90
        )
        out = (res.stdout + "\n" + res.stderr).strip()
        return {
            "ran": True,
            "exit_code": res.returncode,
            "status": "pass" if res.returncode == 0 else "fail",
            "output": out[-2000:],
            "command": " ".join(cmd),
        }
    except subprocess.TimeoutExpired:
        return {"ran": True, "exit_code": -1, "status": "fail", "output": "pytest timeout"}


def _run_lint(repo_root: Path, paths: List[str]) -> Dict[str, Any]:
    py_paths = [p for p in paths if p.endswith(".py")]
    if not py_paths:
        return {"ran": False, "status": "skipped", "output": "no python files to lint"}
    ruff = shutil.which("ruff")
    if not ruff:
        # fallback to py_compile (already done implicitly); call it again here
        errors = []
        for p in py_paths:
            ok, msg = _check_file_exists_and_compiles(repo_root, p)
            if not ok:
                errors.append(msg)
        return {
            "ran": True,
            "status": "pass" if not errors else "fail",
            "output": "\n".join(errors) or "py_compile only",
        }
    try:
        res = subprocess.run(
            [ruff, "check", *py_paths],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "ran": True,
            "status": "pass" if res.returncode == 0 else "fail",
            "output": (res.stdout + res.stderr)[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"ran": True, "status": "fail", "output": "ruff timeout"}


def _evaluate_criteria_rule(
    criteria: List[str], applied_paths: List[str], repo_root: Path
) -> List[Dict[str, Any]]:
    """Heuristic acceptance evaluation."""
    results: List[Dict[str, Any]] = []
    for c in criteria:
        c_lower = c.lower()
        met = False
        evidence = ""
        # criterion mentions a path -> check existence/compile
        path_hits = [p for p in applied_paths if p and p in c]
        if not path_hits:
            # match by file name fragments
            for p in applied_paths:
                stem = Path(p).name
                if stem and stem in c:
                    path_hits.append(p)

        if path_hits:
            for p in path_hits:
                ok, msg = _check_file_exists_and_compiles(repo_root, p)
                met = met or ok
                evidence += msg + "; "
        elif "exists" in c_lower or "syntactically valid" in c_lower:
            # generic check on every applied path
            if applied_paths:
                all_ok = True
                for p in applied_paths:
                    ok, msg = _check_file_exists_and_compiles(repo_root, p)
                    all_ok = all_ok and ok
                    evidence += msg + "; "
                met = all_ok
        elif "public callable" in c_lower:
            for p in applied_paths:
                if p.endswith(".py"):
                    try:
                        src = (repo_root / p).read_text(encoding="utf-8")
                        if "def " in src:
                            met = True
                            evidence += f"public def found in {p}; "
                            break
                    except OSError:
                        pass
        elif "lint" in c_lower or "py_compile" in c_lower:
            lint = _run_lint(repo_root, applied_paths)
            met = lint["status"] in ("pass", "skipped")
            evidence = f"lint:{lint['status']}"
        elif "documentation" in c_lower or "section" in c_lower:
            for p in applied_paths:
                if p.endswith(".md") and (repo_root / p).exists():
                    met = True
                    evidence += f"doc updated: {p}; "
                    break
        elif "tests" in c_lower and "pass" in c_lower:
            pt = _run_pytest(repo_root)
            met = pt["status"] == "pass"
            evidence = f"pytest:{pt['status']}"
        else:
            # weak default: if any file applied without errors, consider met
            met = bool(applied_paths)
            evidence = "no specific check; presence of applied changes"

        results.append({"text": c, "met": bool(met), "evidence": evidence.strip("; ")})
    return results


def _cohesion(
    criteria_results: List[Dict[str, Any]],
    test_status: str,
    regression_ok: bool,
    lint_status: str,
    weights: Dict[str, int],
) -> float:
    if criteria_results:
        met = sum(1 for r in criteria_results if r.get("met"))
        accept_score = met / len(criteria_results)
    else:
        accept_score = 0.0

    if test_status == "pass":
        test_score = 1.0
    elif test_status == "skipped":
        test_score = 0.7  # neutral when no tests exist
    else:
        test_score = 0.0

    regression_score = 1.0 if regression_ok else 0.0

    if lint_status == "pass":
        quality_score = 1.0
    elif lint_status == "skipped":
        quality_score = 0.7
    else:
        quality_score = 0.0

    total = (
        accept_score * weights.get("acceptance", 40)
        + test_score * weights.get("tests", 30)
        + regression_score * weights.get("regression", 20)
        + quality_score * weights.get("quality", 10)
    )
    return round(total, 2)


def run(
    task: Dict[str, Any],
    spec: Dict[str, Any],
    dev_result: Dict[str, Any],
    llm: LLMClient,
    repo_root: Path,
    persona_mode: str,
    weights: Dict[str, int],
) -> Dict[str, Any]:
    applied = dev_result.get("applied", []) or []
    applied_paths = [a["path"] for a in applied if a.get("path")]
    criteria = spec.get("acceptance_criteria") or []

    # Tests
    test_run = _run_pytest(repo_root)
    # Lint
    lint_run = _run_lint(repo_root, applied_paths)
    # Regression: ensure no forbidden path was touched (already enforced) and
    # all applied files compile (for .py)
    regression_ok = True
    for p in applied_paths:
        if p.endswith(".py"):
            ok, _ = _check_file_exists_and_compiles(repo_root, p)
            if not ok:
                regression_ok = False
                break

    criteria_results: List[Dict[str, Any]] = []
    mode_used = "rule"

    if persona_mode in ("llm", "hybrid") and criteria:
        try:
            payload = {
                "task": {"id": task["id"], "text": task["normalized_text"]},
                "spec": spec,
                "applied": applied,
                "tests": test_run,
                "lint": lint_run,
            }
            res = llm.call(
                SYSTEM_PROMPT,
                "Evaluation payload:\n" + json.dumps(payload, indent=2),
                session_id=f"evaluator-{task['id']}",
            )
            parsed = LLMClient.extract_json(res.text)
            if parsed and isinstance(parsed.get("criteria"), list):
                criteria_results = parsed["criteria"]
                regression_ok = bool(parsed.get("regression_ok", regression_ok))
                mode_used = "llm"
        except LLMUnavailable as e:
            if persona_mode == "llm":
                raise
            logger.info("evaluator: LLM unavailable (%s); falling back to rule mode", e)

    if not criteria_results:
        criteria_results = _evaluate_criteria_rule(criteria, applied_paths, repo_root)

    score = _cohesion(criteria_results, test_run["status"], regression_ok, lint_run["status"], weights)

    return {
        "criteria_results": criteria_results,
        "tests": test_run,
        "lint": lint_run,
        "regression_ok": regression_ok,
        "cohesion_score": score,
        "mode_used": mode_used,
    }
