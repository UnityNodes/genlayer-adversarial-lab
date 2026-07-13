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

- Asimov and Bradbury are both live and are SEPARATE networks. They share chainId 4221 and a similar block height, but have different consensus mainContracts (Asimov 0x6CAFF6769d70824745AD895663409DC70aB5B28E, Bradbury 0x0112Bf6e83497965A5fdD6Dad1E447a6E004271D) and separate state: a contract deployed on one is not found on the other (verified). The funded placeholder account holds ~23.8 GEN on both.
- The PoCs are deployed to BOTH so evidence exists whichever network the program credits; confirm the preferred one on portal.genlayer.foundation.
- RPC: https://rpc-asimov.genlayer.com  or  https://rpc-bradbury.genlayer.com
- Explorer scheme: https://explorer-asimov.genlayer.com/address/<contract> (and /tx/<hash>); same paths on explorer-bradbury.

## Testnet PoC evidence (Task 1.11)

Deployed the flagship vulnerable contracts to BOTH testnets and confirmed each on-chain with `genlayer schema`.

**Asimov**
- `web_price_oracle` (`WebPriceOracle`) address `0xBf8392c2A5B5969508217434f2dB248EF7431D8A`, deploy tx `0xb26d469b5a839991e7d734a95bb1f35dbfc10f5a5c3d7579f05acabc8852d8cb`
  - https://explorer-asimov.genlayer.com/address/0xBf8392c2A5B5969508217434f2dB248EF7431D8A
- `sentiment_escrow` (`SentimentEscrow`) address `0xB8877B9aCE25E86B887E67dC9EeD6B8c95734410`, deploy tx `0xd4b955d64ac201b56621a89f31947d0975a7b5c347defc8ad2e5b6b1530f72c2`
  - https://explorer-asimov.genlayer.com/address/0xB8877B9aCE25E86B887E67dC9EeD6B8c95734410
- `judge_bypass` (`JudgeBypass`) address `0xC5674E4e17A03A8b2e7c8CE35Fa289C923855F5A`
  - https://explorer-asimov.genlayer.com/address/0xC5674E4e17A03A8b2e7c8CE35Fa289C923855F5A
- `image_moderator` (`ImageModerator`) address `0xc44BE39b45453d80aDBFfcCA983531987e37Afd2`
  - https://explorer-asimov.genlayer.com/address/0xc44BE39b45453d80aDBFfcCA983531987e37Afd2

**Bradbury**
- `web_price_oracle` (`WebPriceOracle`) address `0x7B9088Ef4c39CB3A36F45b1cAE6eaBF70Af0E29A`, deploy tx `0x1dd9d0d89cbfb1ab8f977c83084526c6c75dd11727cb422504fe75e0e13fde59`
  - https://explorer-bradbury.genlayer.com/address/0x7B9088Ef4c39CB3A36F45b1cAE6eaBF70Af0E29A
- `sentiment_escrow` (`SentimentEscrow`) address `0x8E833c826Ba202Ad5De0168aeF4d56A237b0FbC4`, deploy tx `0x10fb6f0de913dec5b5188b48d946fc1cc7183ecde7adac49b47a622b353f82e2`
  - https://explorer-bradbury.genlayer.com/address/0x8E833c826Ba202Ad5De0168aeF4d56A237b0FbC4
- `judge_bypass` (`JudgeBypass`) address `0x7d933647f97e4C42c358BF9FcE1a4B0e805AC558`
  - https://explorer-bradbury.genlayer.com/address/0x7d933647f97e4C42c358BF9FcE1a4B0e805AC558
- `image_moderator` (`ImageModerator`) address `0x6a7F6b1E752F37F4189E5f79DDE84d7f31B788e0`
  - https://explorer-bradbury.genlayer.com/address/0x6a7F6b1E752F37F4189E5f79DDE84d7f31B788e0

### How the deploy was done (reproducible)

- The pinned Python client (`genlayer-py 0.18`, the latest release) CANNOT deploy to the current testnet: it fails to decode the consensus contract's `getTransactionData` response (client is behind the live testnet). Use the newer Node CLI instead.
- Deploy path that works:
  ```bash
  genlayer network set testnet-asimov
  genlayer account import --name default --private-key <KEY> --password <PW>
  printf '<PW>\n' | genlayer deploy --contract contracts/vulnerable/<name>.py
  ```
- Deployer here is the funded public dev placeholder `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (~23.8 GEN), NOT the `0xFearless-1` identity. To attribute the deploy to your own wallet, import your funded key as the `default` account and redeploy; the addresses above then just get superseded by your own.
