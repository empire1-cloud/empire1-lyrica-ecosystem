"""Tests for App-level JWT construction (app/services/github_app_auth.py).
Uses a throwaway, locally-generated RSA keypair — never a real GitHub
App key.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import jwt as pyjwt  # noqa: E402
import pytest  # noqa: E402
from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import rsa  # noqa: E402

from app.services import github_app_auth  # noqa: E402


@pytest.fixture(scope="module")
def test_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return pem, public_pem


def test_build_app_jwt_requires_configuration(monkeypatch):
    monkeypatch.delenv("GITHUB_APP_ID", raising=False)
    monkeypatch.delenv("GITHUB_APP_PRIVATE_KEY", raising=False)
    with pytest.raises(github_app_auth.GitHubAppNotConfigured):
        github_app_auth.build_app_jwt()


def test_build_app_jwt_produces_valid_signed_token(monkeypatch, test_keypair):
    private_pem, public_pem = test_keypair
    monkeypatch.setenv("GITHUB_APP_ID", "999888")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", private_pem)

    token = github_app_auth.build_app_jwt(now=1_700_000_000)

    # Using a fixed `now` for deterministic assertions below, so disable
    # real-time exp/iat validation here — we're checking claim values, not
    # token freshness (that's GitHub's job when it receives the JWT).
    decoded = pyjwt.decode(
        token, public_pem, algorithms=["RS256"],
        options={"verify_exp": False, "verify_iat": False},
    )
    assert decoded["iss"] == "999888"
    assert decoded["iat"] == 1_700_000_000 - 60
    assert decoded["exp"] == 1_700_000_000 + 9 * 60


def test_build_app_jwt_normalizes_escaped_newlines(monkeypatch, test_keypair):
    private_pem, public_pem = test_keypair
    escaped = private_pem.replace("\n", "\\n")
    monkeypatch.setenv("GITHUB_APP_ID", "999888")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", escaped)

    token = github_app_auth.build_app_jwt(now=1_700_000_000)
    # Using a fixed `now` for deterministic assertions below, so disable
    # real-time exp/iat validation here — we're checking claim values, not
    # token freshness (that's GitHub's job when it receives the JWT).
    decoded = pyjwt.decode(
        token, public_pem, algorithms=["RS256"],
        options={"verify_exp": False, "verify_iat": False},
    )
    assert decoded["iss"] == "999888"
