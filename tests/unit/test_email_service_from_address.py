"""tests/unit/test_email_service_from_address.py
Extra unit tests for EmailService FROM address behavior.
"""
from __future__ import annotations

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.unit
async def test_send_uses_default_from_address(monkeypatch):
    """_send should use default noreply address when SENDGRID_FROM_EMAIL is unset."""
    monkeypatch.delenv("SENDGRID_FROM_EMAIL", raising=False)
    monkeypatch.setenv("SENDGRID_API_KEY", "key")

    from app.services import email_service as es
    es = importlib.reload(es)

    with patch("httpx.AsyncClient") as mock_client:
        mock_resp = MagicMock()
        mock_resp.status_code = 202
        mock_resp.text = "Accepted"
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)

        await es._send(to_email="t@example.com", subject="S", html_body="<p>x</p>")

        post_call = mock_client.return_value.__aenter__.return_value.post
        sent_json = post_call.call_args.kwargs["json"]
        assert sent_json["from"]["email"] == "noreply@eduboost.co.za"


@pytest.mark.unit
async def test_send_uses_env_override_from_address(monkeypatch):
    """_send should use SENDGRID_FROM_EMAIL value when provided."""
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "custom@exa.mple")
    monkeypatch.setenv("SENDGRID_API_KEY", "key")

    from app.services import email_service as es
    es = importlib.reload(es)

    with patch("httpx.AsyncClient") as mock_client:
        mock_resp = MagicMock()
        mock_resp.status_code = 202
        mock_resp.text = "Accepted"
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)

        await es._send(to_email="t@example.com", subject="S", html_body="<p>x</p>")

        post_call = mock_client.return_value.__aenter__.return_value.post
        sent_json = post_call.call_args.kwargs["json"]
        assert sent_json["from"]["email"] == "custom@exa.mple"
