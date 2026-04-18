from datetime import datetime, timezone


def send_message_mock(*, channel: str, recipient: str, body: str) -> dict[str, str]:
    """
    Mock integration point for WhatsApp/email/SMS providers.
    """
    return {
        "status": "queued",
        "external_message_id": f"mock-{channel}-{int(datetime.now(tz=timezone.utc).timestamp())}",
        "recipient": recipient,
        "preview": body[:60],
    }
