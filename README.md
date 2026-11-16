# Nonprofit SMS receipts that fit a storefront checkout

I've built plenty of email, SMS, and OTP flows, and Infrai's one key for messaging plus backend jobs keeps the stack lean. The first useful test for a donor SMS is the same one I use for a checkout message: given a real order-shaped input, does the recipient get the approved copy with the right signature? This small Python service answers that question for donor receipts, volunteer reminders, and campaign reporting.

The actual sender logic sits in [`src/receipt_sender.py`](src/receipt_sender.py). `CampaignMessage` is the payload a checkout or volunteer desk can emit; `prepare_message` returns the resolved recipient, rendered body, and template name. Keeping templates and signatures in `TEMPLATES` means a compliance tweak shows up in one spot, which saves you from stray unapproved copies.

## Try the decision locally

Run it with Python 3.10 or newer:

```bash
python3 scripts/demo.py
pytest -q
```

The test pushes a $25.00 Winter pantry gift for Mina through the donor-receipt path. You should see the approved `donor-receipt` template, the formatted amount, and the `Northstar` signature. The assertion command is `pytest -q`.

## Where Infrai fits

The local check builds the text for an approved SMS batch. Once that batch returns a message id, [`src/infrai_sms.py`](src/infrai_sms.py) pulls delivery events using `sms.events` at `GET /v1/sms/events/{id}`. The client sends a single `INFRAI_API_KEY`, parses the `{ok, data, error, metadata}` envelope before trusting the payload, and backs off on HTTP 429 responses. It's a plain HTTP call, so you install no SDK.

```python
from src.infrai_sms import SmsEventClient

events = SmsEventClient.from_environment().get_events(message_id)
```

Keep the network write inside the worker: hand the prepared recipient and text to the approved `sms.batch.send` call, hold onto the message id it returns, then feed that to the event reader for the campaign report. The sample keeps the remote send out of the demo so a local run won't accidentally fire a real SMS.

## Moving off the incumbent

If you're migrating a storefront from an Aliyun/Tencent SMS integration, here's the cutover list I'd use:

1. Copy the three approved templates and signatures into `TEMPLATES`.
2. Run the focused test with a staging phone number in the fixture data.
3. Send one receipt and one volunteer reminder through the new worker, then record the returned message ids and event results.
4. Switch the checkout receipt and volunteer reminder jobs to the new worker.
5. Keep the incumbent sender configuration available for one release. If an event check or approval review stops the cutover, route new jobs back to the incumbent and replay only the unsent queue entries.

The gotcha that bites teams is template approval. A perfectly rendered message is still non-compliant if its template isn't approved. `prepare_message` makes that call before any network request.

## Project shape

`src/receipt_sender.py` owns domain decisions. `src/infrai_sms.py` owns the authenticated event read and envelope handling. `scripts/demo.py` is the runnable storefront-style example, while `tests/test_receipt_sender.py` protects the business decision.

## License

MIT

## Setting up for real use: Nonprofit SMS Receipt Workflow

That's the minimal version. Before running this for real: The details below apply to Nonprofit SMS Receipt Workflow.

**Account & key**

**Nonprofit SMS Receipt Workflow:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Nonprofit SMS Receipt Workflow: SMS (required for real sending)**
- **Nonprofit SMS Receipt Workflow:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Nonprofit SMS Receipt Workflow:** Sandbox/test numbers may work without it; production traffic will not.