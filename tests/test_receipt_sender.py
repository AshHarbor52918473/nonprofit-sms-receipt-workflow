from src.receipt_sender import CampaignMessage, prepare_message


def test_donor_receipt_uses_approved_template_and_signature() -> None:
    result = prepare_message(
        CampaignMessage("donor_receipt", "+15550101", "Mina", 2500, "Winter pantry")
    )

    assert result.template_name == "donor-receipt"
    assert result.text == "Thanks Mina for your $25.00 gift to Winter pantry. Reply STOP to opt out. - Northstar"

