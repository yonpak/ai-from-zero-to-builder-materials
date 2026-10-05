#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path


def fail(msg):
    raise AssertionError(msg)


def load_module(path):
    spec = importlib.util.spec_from_file_location("p15_submission", path)
    if spec is None or spec.loader is None:
        fail("cannot import submission")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect_value_error(fn, msg):
    try:
        fn()
    except ValueError:
        return
    fail(msg)


def objective_checks(m, run):
    required = [
        "regression_summary",
        "human_review_summary",
        "authorize_action",
        "deletion_eligible",
        "threat_summary",
        "frontier_claim_valid",
        "reproduction_record_valid",
        "evidence_summary",
        "release_allowed",
        "validate_run",
    ]
    for name in required:
        if not callable(getattr(m, name, None)):
            fail("missing callable " + name)

    reg = m.regression_summary([
        {"id":"a","passed":True,"critical":False},
        {"id":"b","passed":True,"critical":False},
        {"id":"c","passed":False,"critical":True},
    ])
    if reg["critical_regressions"] != 1 or abs(reg["regression_success"] - 2/3) > 0.001:
        fail("regression summary contract failed")

    human = m.human_review_summary([
        {"case_id":"x","reviewer":"r1","score":1},
        {"case_id":"x","reviewer":"r2","score":5},
    ])
    if human["high_disagreement_cases"] != 1 or human["human_mean_score"] != 3.0:
        fail("human review summary contract failed")

    principal = {"role":"support"}
    policy = {"support":["read_order"], "admin":["read_order","refund_order"]}
    if not m.authorize_action(principal, {"action":"read_order","role":"admin"}, policy):
        fail("allowed action rejected")
    if m.authorize_action(principal, {"action":"refund_order","role":"admin"}, policy):
        fail("generated role incorrectly changed authority")

    if not m.deletion_eligible({"created_day":0,"retention_days":30,"legal_hold":False}, 31):
        fail("expired record not eligible")
    if m.deletion_eligible({"created_day":0,"retention_days":30,"legal_hold":True}, 31):
        fail("legal hold ignored")

    threats = m.threat_summary([
        {
            "category":"jailbreak",
            "severity":"critical",
            "expected":"blocked",
            "observed":"executed",
        },
        {
            "category":"ordinary_input_validation",
            "severity":"medium",
            "expected":"rejected",
            "observed":"rejected",
        },
    ])
    if threats["critical_threat_failures"] != 1:
        fail("critical threat failure not counted")
    expect_value_error(
        lambda: m.threat_summary([
            {
                "category":"",
                "severity":"critical",
                "expected":"blocked",
                "observed":"blocked",
            },
        ]),
        "threat category must be preserved",
    )

    claim = {
        "claim":"bounded claim",
        "evidence_source":"reviewed source",
        "system_version":"v1",
        "snapshot_date":"2026-09-08",
        "scope":"test scope",
        "local_test":"run local suite",
    }
    if not m.frontier_claim_valid(claim, "2026-09-08"):
        fail("valid frontier claim rejected")
    future = dict(claim)
    future["snapshot_date"] = "2026-09-09"
    if m.frontier_claim_valid(future, "2026-09-08"):
        fail("unreviewed future frontier claim accepted")
    malformed = dict(claim)
    malformed["snapshot_date"] = "1"
    if m.frontier_claim_valid(malformed, "2026-09-08"):
        fail("malformed frontier date accepted")

    reproduction = {
        "claim":"candidate improves reduced metric",
        "environment":{"python":"3.11","platform":"cpu"},
        "seed_policy":"fixed seed 13",
        "baseline":0.7,
        "candidate":0.8,
        "expected_relation":"candidate_gt_baseline",
        "conclusion":"partially_reproduced",
    }
    if not m.reproduction_record_valid(reproduction):
        fail("valid reproduction record rejected")
    contradictory = dict(reproduction)
    contradictory["candidate"] = 0.6
    contradictory["conclusion"] = "confirmed_in_scope"
    if m.reproduction_record_valid(contradictory):
        fail("reproduction conclusion contradicted its numeric evidence")
    not_reproduced = dict(contradictory)
    not_reproduced["conclusion"] = "not_reproduced"
    if not m.reproduction_record_valid(not_reproduced):
        fail("not-reproduced conclusion rejected when expected relation failed")

    artifacts = [
        {
            "artifact_id":"base-model",
            "artifact":"base-model",
            "revision":"r1",
            "source":"registry",
            "license_or_terms":"model-license-v2",
            "terms_reviewed":True,
            "review_evidence":"license-review-17",
        },
        {
            "artifact_id":"application-code",
            "artifact":"app-code",
            "revision":"c1",
            "source":"repository",
            "license_or_terms":"repository-license",
            "terms_reviewed":True,
            "review_evidence":"code-review-18",
        },
    ]
    obligations = [
        {
            "requirement_id":"external-obligations-review",
            "requirement":"record applicable obligations",
            "applicable":True,
            "owner":"compliance",
            "evidence":"review-22",
            "reviewed_date":"2026-10-02",
        },
        {
            "requirement_id":"scope-review",
            "requirement":"record out-of-scope reasoning",
            "applicable":False,
            "owner":"compliance",
            "evidence":"scope-review-23",
            "reviewed_date":"2026-10-02",
        },
    ]
    required_artifacts = ["base-model", "application-code"]
    required_obligations = ["external-obligations-review", "scope-review"]
    evidence = m.evidence_summary(
        artifacts,
        obligations,
        required_artifacts,
        required_obligations,
    )
    if evidence != {
        "artifact_evidence_violations":0,
        "governance_evidence_violations":0,
    }:
        fail("valid release evidence rejected")

    missing_artifact = artifacts[:1]
    evidence = m.evidence_summary(
        missing_artifact,
        obligations,
        required_artifacts,
        required_obligations,
    )
    if evidence["artifact_evidence_violations"] == 0:
        fail("missing required artifact inventory entry not counted")

    missing_obligation = obligations[:1]
    evidence = m.evidence_summary(
        artifacts,
        missing_obligation,
        required_artifacts,
        required_obligations,
    )
    if evidence["governance_evidence_violations"] == 0:
        fail("missing required governance inventory entry not counted")

    broken_artifacts = json.loads(json.dumps(artifacts))
    broken_artifacts[0]["license_or_terms"] = ""
    evidence = m.evidence_summary(
        broken_artifacts,
        obligations,
        required_artifacts,
        required_obligations,
    )
    if evidence["artifact_evidence_violations"] == 0:
        fail("missing license/terms identifier not counted")

    broken_obligations = json.loads(json.dumps(obligations))
    broken_obligations[0]["reviewed_date"] = "yesterday"
    evidence = m.evidence_summary(
        artifacts,
        broken_obligations,
        required_artifacts,
        required_obligations,
    )
    if evidence["governance_evidence_violations"] == 0:
        fail("malformed governance review date not counted")

    good = {
        "regression_success":1.0,
        "critical_regressions":0,
        "human_mean_score":4.5,
        "high_disagreement_cases":0,
        "unauthorized_actions":0,
        "retention_violations":0,
        "critical_threat_failures":0,
        "frontier_evidence_violations":0,
        "reproduction_evidence_violations":0,
        "artifact_evidence_violations":0,
        "governance_evidence_violations":0,
    }
    if not m.release_allowed(good, run["release_rule"]):
        fail("passing release metrics rejected")
    blocked = dict(good)
    blocked["artifact_evidence_violations"] = 1
    if m.release_allowed(blocked, run["release_rule"]):
        fail("artifact evidence violation did not block release")

    m.validate_run(run)

    tampered = json.loads(json.dumps(run))
    tampered["regression_cases"][2]["passed"] = False
    expect_value_error(lambda: m.validate_run(tampered), "critical regression tamper must reject")

    tampered = json.loads(json.dumps(run))
    tampered["actions"][1]["executed"] = True
    expect_value_error(lambda: m.validate_run(tampered), "unauthorized execution must reject")

    tampered = json.loads(json.dumps(run))
    tampered["records"][0]["retained"] = True
    expect_value_error(lambda: m.validate_run(tampered), "retention violation must reject")

    tampered = json.loads(json.dumps(run))
    tampered["frontier_claims"][0]["system_version"] = ""
    expect_value_error(lambda: m.validate_run(tampered), "unscoped frontier evidence must reject")

    tampered = json.loads(json.dumps(run))
    tampered["frontier_claims"][0]["snapshot_date"] = "not-a-date"
    expect_value_error(lambda: m.validate_run(tampered), "malformed frontier date must reject")

    tampered = json.loads(json.dumps(run))
    tampered["threat_tests"][0]["category"] = ""
    expect_value_error(lambda: m.validate_run(tampered), "missing threat category must reject")

    tampered = json.loads(json.dumps(run))
    tampered["artifact_evidence"] = tampered["artifact_evidence"][:1]
    expect_value_error(lambda: m.validate_run(tampered), "missing required artifact row must reject")

    tampered = json.loads(json.dumps(run))
    tampered["governance_obligations"] = tampered["governance_obligations"][:1]
    expect_value_error(lambda: m.validate_run(tampered), "missing required governance row must reject")

    tampered = json.loads(json.dumps(run))
    tampered["artifact_evidence"][0]["license_or_terms"] = ""
    expect_value_error(lambda: m.validate_run(tampered), "missing artifact terms must reject")

    tampered = json.loads(json.dumps(run))
    tampered["governance_obligations"][0]["evidence"] = ""
    expect_value_error(lambda: m.validate_run(tampered), "missing governance evidence must reject")

    tampered = json.loads(json.dumps(run))
    tampered["reproductions"][0]["candidate"] = 0.1
    expect_value_error(lambda: m.validate_run(tampered), "contradictory reproduction evidence must reject")

    blocked_run = json.loads(json.dumps(run))
    blocked_run["regression_cases"][2]["passed"] = False
    blocked_run["metrics"]["regression_success"] = 0.8
    blocked_run["metrics"]["critical_regressions"] = 1
    blocked_run["release_passed"] = False
    expect_value_error(
        lambda: m.validate_run(blocked_run),
        "recomputed critical regression must block release",
    )

    tampered = json.loads(json.dumps(run))
    tampered["release_passed"] = False
    expect_value_error(lambda: m.validate_run(tampered), "release flag must be recomputed")


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_submission.py SUBMISSION.py CAPSTONE-RUN.json")
    module = load_module(Path(sys.argv[1]))
    data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    objective_checks(module, data)
    print("PASS: p15-ai-product-capstone objective checks")


if __name__ == "__main__":
    main()
