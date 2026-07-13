# Deploy notes

## End-to-end baseline: studionet (Task 0.3 / 1.10)

Ran integration against the hosted GenLayer Studio, no local Docker:

```bash
gltest --network studionet tests/integration/ -v -s
```

- RPC: https://studio.genlayer.com/api (account auto-provisioned by the host)
- Result: both integration tests PASS on a real hosted node.
  - `test_oracle_deploys` (deploy WebPriceOracle + consensus read `get_price`): PASS, ~16s.
  - `test_escrow_submit_review_end_to_end` (SentimentEscrow `submit_review`: exec_prompt + strict_eq consensus + state write): PASS, ~30s.
- Note: `web_price_oracle.settle` end-to-end is model-dependent - a real model reading a live page does not reliably return a bare integer, so `int(...)` can revert. That sink's adversarial proof lives in Direct mode (`tests/direct/test_web_price_oracle_vulnerable.py`), which deterministically simulates the poisoned page. This nondeterminism on borderline model output is itself the consensus-split / liveness class from the attack corpus.

Local Studio (`genlayer up`) is intentionally skipped: on a headless server it still needs a model backend (Ollama or an API key), while studionet supplies the model and needs no Docker.

## Testnet target (Task 0.4)

- Live network: _Asimov | Bradbury_ (confirm on portal.genlayer.foundation)
- RPC: https://rpc-asimov.genlayer.com  or  https://rpc-bradbury.genlayer.com
- Explorer: https://explorer-asimov.genlayer.com  or  https://explorer-bradbury.genlayer.com

## Testnet PoC evidence (Task 1.11)

studionet deploys are ephemeral and NOT portal evidence. For submissions, deploy the flagship
vulnerable contracts to the chosen testnet (funded key in `.env`) and record the Explorer URLs here.

- `web_price_oracle`: _address_ / _explorer url_
- `sentiment_escrow`: _address_ / _explorer url_
