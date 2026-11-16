import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.receipt_sender import CampaignMessage, prepare_message


def main() -> None:
    message = prepare_message(
        CampaignMessage(
            kind="donor_receipt",
            recipient="+15550101",
            donor_name="Mina",
            amount_cents=2500,
            campaign_name="Winter pantry",
        )
    )
    print(message)
    print("Ready for sms.batch.send with the approved text above.")


if __name__ == "__main__":
    main()
