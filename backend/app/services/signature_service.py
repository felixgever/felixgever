from datetime import datetime, timezone


def request_signature_mock(*, resident_id: int, provider: str) -> dict[str, str]:
    """
    Mock integration point for digital signature vendors.
    """
    ref = f"{provider}-resident-{resident_id}-{int(datetime.now(tz=timezone.utc).timestamp())}"
    return {"status": "requested", "external_reference": ref}
