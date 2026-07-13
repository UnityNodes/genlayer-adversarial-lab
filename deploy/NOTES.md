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

- Live network: Asimov (chainId 4221). Both rpc-asimov and rpc-bradbury answer with the same chainId and near-identical block height, so they front the same current testnet; confirm the program's preferred name on portal.genlayer.foundation.
- RPC: https://rpc-asimov.genlayer.com  (mainContract 0x6CAFF6769d70824745AD895663409DC70aB5B28E)
- Explorer scheme: https://explorer-asimov.genlayer.com/address/<contract>  and  /tx/<hash>

## Testnet PoC evidence (Task 1.11)

Deployed the flagship vulnerable contracts to Asimov and confirmed each on-chain with `genlayer schema`.

- `web_price_oracle` (`WebPriceOracle`)
  - address: `0xBf8392c2A5B5969508217434f2dB248EF7431D8A`
  - deploy tx: `0xb26d469b5a839991e7d734a95bb1f35dbfc10f5a5c3d7579f05acabc8852d8cb`
  - explorer: https://explorer-asimov.genlayer.com/address/0xBf8392c2A5B5969508217434f2dB248EF7431D8A
- `sentiment_escrow` (`SentimentEscrow`)
  - address: `0xB8877B9aCE25E86B887E67dC9EeD6B8c95734410`
  - deploy tx: `0xd4b955d64ac201b56621a89f31947d0975a7b5c347defc8ad2e5b6b1530f72c2`
  - explorer: https://explorer-asimov.genlayer.com/address/0xB8877B9aCE25E86B887E67dC9EeD6B8c95734410

### How the deploy was done (reproducible)

- The pinned Python client (`genlayer-py 0.18`, the latest release) CANNOT deploy to the current testnet: it fails to decode the consensus contract's `getTransactionData` response (client is behind the live testnet). Use the newer Node CLI instead.
- Deploy path that works:
  ```bash
  genlayer network set testnet-asimov
  genlayer account import --name default --private-key <KEY> --password <PW>
  printf '<PW>\n' | genlayer deploy --contract contracts/vulnerable/<name>.py
  ```
- Deployer here is the funded public dev placeholder `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (~23.8 GEN), NOT the `0xFearless-1` identity. To attribute the deploy to your own wallet, import your funded key as the `default` account and redeploy; the addresses above then just get superseded by your own.
