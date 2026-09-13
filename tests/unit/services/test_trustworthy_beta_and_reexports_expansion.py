from __future__ import annotations

import pytest

import app.services.archetype_service as archetype_service_mod
import app.services.consent as consent_mod
import app.services.diagnostic as diagnostic_mod
import app.services.ether as ether_mod
import app.services.executive as executive_mod
import app.services.fourth_estate as fourth_estate_mod
import app.services.judiciary as judiciary_mod
import app.services.lesson_generator as lesson_generator_mod
import app.services.rlhf_service as rlhf_service_mod
import app.services.trustworthy_beta_quality as tbq


def test_trustworthy_beta_quality():
    keys = tbq.trustworthy_beta_quality_keys()
    assert isinstance(keys, list)
    assert len(keys) > 0

    # Incomplete keys set
    assert tbq.trustworthy_beta_quality_complete(set()) is False
    assert tbq.trustworthy_beta_quality_complete({keys[0]}) is False

    # Complete keys set
    assert tbq.trustworthy_beta_quality_complete(set(keys)) is True

    # Superset
    assert tbq.trustworthy_beta_quality_complete(set(keys) | {"extra_key"}) is True


def test_rlhf_service_formats():
    svc = rlhf_service_mod.RLHFService()
    records = [{"input": "Hello", "output": "World"}]

    openai_res = svc.export_openai_format(records)
    assert openai_res["format"] == "openai"
    assert openai_res["record_count"] == 1
    assert "dataset_json" in openai_res

    anthropic_res = svc.export_anthropic_format(records)
    assert anthropic_res["format"] == "anthropic"
    assert anthropic_res["record_count"] == 1
    assert "dataset_json" in anthropic_res


def test_service_reexport_shims():
    # archetype_service
    assert hasattr(archetype_service_mod, "ArchetypeService")

    # consent
    assert hasattr(consent_mod, "ConsentService")

    # diagnostic
    assert hasattr(diagnostic_mod, "DiagnosticEngine")
    assert hasattr(diagnostic_mod, "p_correct")
    assert hasattr(diagnostic_mod, "update_theta_mle")

    # ether
    assert hasattr(ether_mod, "EtherService")

    # executive
    assert hasattr(executive_mod, "ExecutiveService")

    # fourth_estate
    assert hasattr(fourth_estate_mod, "FourthEstateService")

    # judiciary
    assert hasattr(judiciary_mod, "ConstitutionalViolation")
    assert hasattr(judiciary_mod, "JudiciaryService")
    assert hasattr(judiciary_mod, "LessonPayload")

    # lesson_generator
    assert hasattr(lesson_generator_mod, "LessonGenerator")
    assert hasattr(lesson_generator_mod, "QuotaExceededError")
