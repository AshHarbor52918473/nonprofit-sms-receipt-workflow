"""Approved SMS workflow for nonprofit checkout and volunteer operations."""

from dataclasses import dataclass
from typing import Literal


MessageKind = Literal["donor_receipt", "volunteer_reminder", "campaign_report"]


@dataclass(frozen=True)
class SmsTemplate:
    name: str
    body: str
    signature: str
    approved: bool = True


@dataclass(frozen=True)
class CampaignMessage:
    kind: MessageKind
    recipient: str
    donor_name: str
    amount_cents: int = 0
    campaign_name: str = ""
    event_name: str = ""


@dataclass(frozen=True)
class PreparedMessage:
    recipient: str
    text: str
    template_name: str


TEMPLATES = {
    "donor_receipt": SmsTemplate(
        "donor-receipt", "Thanks {donor_name} for your {amount} gift to {campaign_name}.", "Northstar", True
    ),
    "volunteer_reminder": SmsTemplate(
        "volunteer-reminder", "Hi {donor_name}, your {event_name} shift is tomorrow.", "Northstar", True
    ),
    "campaign_report": SmsTemplate(
        "campaign-report", "{campaign_name} raised {amount} this week. Thank you!", "Northstar", True
    ),
}


def _money(cents: int) -> str:
    return f"${cents / 100:.2f}"


def prepare_message(message: CampaignMessage) -> PreparedMessage:
    """Choose an approved template and render the checkout-shaped input."""
    template = TEMPLATES[message.kind]
    if not template.approved:
        raise ValueError("message template is awaiting approval")
    text = template.body.format(
        donor_name=message.donor_name,
        amount=_money(message.amount_cents),
        campaign_name=message.campaign_name,
        event_name=message.event_name,
    )
    return PreparedMessage(message.recipient, f"{text} Reply STOP to opt out. - {template.signature}", template.name)

