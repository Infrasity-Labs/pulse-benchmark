"""Drives the Okto Pulse staged chain over REST (same server, same gates).

Transport note: the pi MCP bridge serialises array-valued params as strings, so
bulk staged runs are driven through the local REST API instead. Every lifecycle
gate is still evaluated server-side; nothing is bypassed or faked.

Per task chain: ideation -> arch + mockup -> review/approved/evaluating/done
  -> refinement (brownfield) -> review/approved/done
  -> derive spec -> fill FR/TR/AC -> review/approved -> implementation card
"""
import json
import sys

from pulse_rest import BOARD, call

DONE = ["review", "approved", "evaluating", "done"]


def _pick(d, *keys):
    """Find the first scalar value stored under any of *keys, recursively."""
    if isinstance(d, dict):
        for k in keys:
            v = d.get(k)
            if isinstance(v, str) and v:
                return v
        for v in d.values():
            r = _pick(v, *keys)
            if r:
                return r
    elif isinstance(d, list):
        for v in d:
            r = _pick(v, *keys)
            if r:
                return r
    return None


def _spec_for_refinement(ref):
    st, res = call("GET", "/boards/%s/specs" % BOARD)
    items = res if isinstance(res, list) else (res or {}).get("items", [])
    for i in items or []:
        if i.get("refinement_id") == ref:
            return i.get("id")
    return None


def log(res, step, out):
    ok = res[0] in (200, 201)
    if not ok:
        out.append("GATE-FAIL %s: %s" % (step, str(res[1])[:160]))
    return ok, (res[1] or {})


def run(t, out):
    iid, path = t["iid"], t["path"]
    # 1. ideation
    if t.get("ideation_id"):
        ide = t["ideation_id"]
    else:
        st, b = log(
            call(
                "POST",
                "/boards/%s/ideations" % BOARD,
                {
                    "title": t["i_title"],
                    "description": t["i_desc"],
                    "problem_statement": t["i_prob"],
                    "proposed_approach": t["i_appr"],
                    "labels": ["swebench", "pytest", "staged"],
                },
            ),
            "create ideation",
            out,
        )
        if not st:
            return None
        ide = b["ideation"]["id"] if "ideation" in b else b["id"]

    # 2. mandatory gate resources (architecture + mockup)
    if not t.get("resources_done"):
        log(
            call(
                "POST",
                "/ideations/%s/architecture" % ide,
                {"title": t["a_title"], "global_description": t["a_desc"]},
            ),
            "architecture",
            out,
        )
        log(
            call(
                "POST",
                "/ideations/%s/screen-mockups" % ide,
                {
                    "title": t["m_title"],
                    "description": "Text mock of rendered output before vs after (no GUI).",
                    "screen_type": "page",
                    "html_content": t["m_html"],
                    "entity_type": "ideation",
                },
            ),
            "mockup",
            out,
        )
    if t.get("skip_ideation_moves"):
        moves = []
    elif "ideation_moves" in t:
        moves = t["ideation_moves"]
    elif t.get("ideation_id"):
        moves = ["approved", "evaluating", "done"]
    else:
        moves = DONE
    for mv in moves:
        ok, _ = log(
            call("POST", "/ideations/%s/move" % ide, {"status": mv}), "ideation->" + mv, out
        )
        if not ok:
            return None

    # 3. refinement
    if t.get("refinement_id"):
        ref = t["refinement_id"]
    else:
        st, b = log(
            call(
                "POST",
                "/ideations/%s/refinements" % ide,
                {
                    "ideation_id": ide,
                    "title": t["r_title"],
                    "description": t["r_desc"],
                    "analysis": t["r_analysis"],
                    "in_scope": t["r_in"],
                    "out_of_scope": t["r_out"],
                    "decisions": t["r_dec"],
                    "delivery_context": "brownfield",
                },
            ),
            "create refinement",
            out,
        )
        if not st:
            return None
        ref = b["refinement"]["id"] if "refinement" in b else b["id"]
    for mv in ([] if t.get("skip_refinement_moves")
               else t.get("refinement_moves", ["review", "approved", "done"])):
        ok, _ = log(call("POST", "/refinements/%s/move" % ref, {"status": mv}), "ref->" + mv, out)
        if not ok:
            return None

    # 4. spec
    spec = t.get("spec_id")
    if not spec:
        st, b = log(
            call(
                "POST",
                "/refinements/%s/derive-spec" % ref,
                {
                    "knowledge_propagation": {
                        "contract_version": 2,
                        "selection_state": "omitted",
                        "idempotency_key": "kp-%s" % t["iid"],
                    }
                },
            ),
            "derive spec",
            out,
        )
        spec = _pick(b, "spec_id") or _spec_for_refinement(ref)
        if not spec:
            return None
    log(
        call(
            "PATCH",
            "/specs/%s" % spec,
            {
                "functional_requirements": t["s_fr"],
                "technical_requirements": t["s_tr"],
                "acceptance_criteria": t["s_ac"],
            },
        ),
        "fill spec",
        out,
    )
    for mv in ["review", "approved"]:
        ok, _ = log(call("POST", "/specs/%s/move" % spec, {"status": mv}), "spec->" + mv, out)
        if not ok:
            return None

    # 5. implementation task card
    st, b = log(
        call(
            "POST",
            "/boards/%s/cards" % BOARD,
            {
                "title": t["c_title"],
                "description": t["c_desc"],
                "details": t["c_details"]
                % {"iid": iid, "path": path},
                "spec_id": spec,
                "priority": "medium",
                "labels": ["swebench", "pytest", "staged"],
            },
        ),
        "create card",
        out,
    )
    if not st:
        return None
    card = _pick(b, "card_id", "id")
    if not card:
        return None

    return {"ideation": ide, "refinement": ref, "spec": spec, "card": card}


if __name__ == "__main__":
    tasks = json.load(open(sys.argv[1]))
    results = {}
    for t in tasks:
        out = []
        try:
            r = run(t, out)
        except Exception as e:
            r, out = None, ["EXC %s: %s" % (type(e).__name__, str(e)[:150])]
        results[t["iid"]] = {"ok": bool(r), "ids": r, "gate_notes": out}
        print(
            "%-28s %s  %s"
            % (
                t["iid"],
                "STAGED-OK" if r else "STAGED-INCOMPLETE",
                "" if not out else " | ".join(out)[:220],
            )
        )
    json.dump(results, open(sys.argv[2], "w"), indent=1)
