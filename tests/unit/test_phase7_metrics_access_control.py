from app.api_v2 import _is_private_metrics_client


def test_metrics_access_allows_loopback_and_rfc1918_addresses() -> None:
    assert _is_private_metrics_client("127.0.0.1")
    assert _is_private_metrics_client("10.20.30.40")
    assert _is_private_metrics_client("172.16.0.1")
    assert _is_private_metrics_client("172.31.255.254")
    assert _is_private_metrics_client("192.168.1.10")
    assert _is_private_metrics_client("::1")


def test_metrics_access_rejects_public_and_invalid_addresses() -> None:
    assert not _is_private_metrics_client("8.8.8.8")
    assert not _is_private_metrics_client("172.15.255.255")
    assert not _is_private_metrics_client("172.32.0.1")
    assert not _is_private_metrics_client("")
    assert not _is_private_metrics_client("not-an-ip")
