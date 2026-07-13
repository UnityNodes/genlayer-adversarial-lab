# genlayer-adversarial-lab

A runnable adversarial-testing lab for **GenLayer Intelligent Contracts**: vulnerable-by-design target contracts, their hardened counterparts, and a Direct-mode test suite that demonstrates prompt-injection attacks and the defenses that stop them — plus a roadmap toward empirical greyboxing measurement.

> **Status: 🟡 work in progress.** Toolchain scaffold and architecture are in place. Contracts, tests and reports are being implemented on a Linux environment (Python 3.12 + Docker). See [SETUP.md](SETUP.md).

> **Responsible use.** Every artifact here is for **defensive security research and education**. Attack contracts and payloads target lab-controlled contracts and mocks only — never third-party deployments. No real users, funds, or systems are involved.

## What it explores

GenLayer Intelligent Contracts can call LLMs and fetch the web without oracles. That creates three concrete injection sinks, one per target contract:

| Target | Sink | Demonstrates |
|--------|------|--------------|
| `sentiment_escrow` | user argument → `exec_prompt` | direct prompt injection; a deterministic jailbreak passes `strict_eq` consensus |
| `web_price_oracle` | fetched web content → `exec_prompt` | indirect (second-order) injection; every validator ingests the same poisoned page |
| `judge_bypass` | attacker text → equivalence-principle criteria | the LLM judge itself is subverted |

Each ships in two variants:
- **vulnerable/** — naive: untrusted data concatenated into the prompt; the model's verdict trusted directly.
- **hardened/** — strict JSON-schema output, deterministic guards in Python, independent validator judging.

The lab's thesis, verified against GenVM source: **consensus only catches non-deterministic divergence between validators. A prompt injection that flips every node the same way passes consensus untouched — so integrity must live in contract logic, not the equivalence principle.** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Structure

```
contracts/vulnerable/   # naive target contracts (one per sink)
contracts/hardened/     # mitigated counterparts
attacks/                # attack corpus as data (payloads + manifests)
tests/direct/           # fast in-memory adversarial tests (LLM/web mocked)
tests/integration/      # Studio end-to-end (real consensus)
reports/findings/       # security findings writeups
docs/ARCHITECTURE.md    # technical foundation
```

## Setup & running

Full environment setup (Python 3.12, GenLayer CLI, Studio via Docker): **[SETUP.md](SETUP.md)**.

```bash
genvm-lint check contracts/vulnerable/*.py contracts/hardened/*.py
pytest tests/direct/ -v                 # fast adversarial tests (no Docker)
gltest tests/integration/ -v -s         # end-to-end on Studio (Docker required)
```

## Built on

The official GenLayer toolchain: [`genlayer-py`](https://github.com/genlayerlabs/genlayer-py), [`genlayer-testing-suite`](https://github.com/genlayerlabs/genlayer-testing-suite) (gltest), [`genvm-linter`](https://github.com/genlayerlabs/genvm-linter), and patterns from the [`genlayer-project-boilerplate`](https://github.com/genlayerlabs/genlayer-project-boilerplate).

## License

MIT — see [LICENSE](LICENSE).
