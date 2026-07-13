# genlayer-adversarial-lab

A runnable adversarial-testing lab for **GenLayer Intelligent Contracts**: vulnerable-by-design target contracts, their hardened counterparts, and a Direct-mode test suite that demonstrates prompt-injection attacks and the defenses that stop them - plus a roadmap toward empirical greyboxing measurement.

> **Status: 🟢 Phase 1 complete; Phase 2 greybox underway.** Four vulnerable/hardened contract pairs, a green Direct-mode suite (24 tests), an attack corpus, source-verified findings, greybox techniques with a tested reference, and PoCs live on both testnets (Asimov and Bradbury). See [SETUP.md](SETUP.md) and [reports/RESEARCH-ANALYSIS.md](reports/RESEARCH-ANALYSIS.md).

> **Responsible use.** Every artifact here is for **defensive security research and education**. Attack contracts and payloads target lab-controlled contracts and mocks only - never third-party deployments. No real users, funds, or systems are involved.

## What it explores

GenLayer Intelligent Contracts can call LLMs and fetch the web without oracles. That creates four concrete injection sinks, one per target contract:

| Target | Sink | Demonstrates |
|--------|------|--------------|
| `sentiment_escrow` | user argument → `exec_prompt` | direct prompt injection; a deterministic jailbreak passes `strict_eq` consensus |
| `web_price_oracle` | fetched web content → `exec_prompt` | indirect (second-order) injection; every validator ingests the same poisoned page |
| `judge_bypass` | attacker text → LLM judge prompt | the LLM judge itself is subverted |
| `image_moderator` | image bytes → `exec_prompt(images=...)` | multimodal injection; text rendered inside an image is unfiltered by default |

Each ships in two variants:
- **vulnerable/** - naive: untrusted data concatenated into the prompt; the model's verdict trusted directly.
- **hardened/** - strict JSON-schema output, deterministic guards in Python, independent validator judging.

The lab's thesis, verified against GenVM source: **consensus only catches non-deterministic divergence between validators. A prompt injection that flips every node the same way passes consensus untouched - so integrity must live in contract logic, not the equivalence principle.** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Structure

```
contracts/vulnerable/   # naive target contracts (one per sink)
contracts/hardened/     # mitigated counterparts
attacks/                # attack corpus as data (payloads + manifests)
tests/direct/           # fast in-memory adversarial tests (LLM/web mocked)
tests/integration/      # Studio end-to-end (real consensus)
greybox/                # validator-side greybox techniques + tested reference
reports/findings/       # security findings writeups
reports/RESEARCH-ANALYSIS.md  # synthesis writeup
deploy/NOTES.md         # testnet deployments and reproduction notes
docs/ARCHITECTURE.md    # technical foundation
```

## Setup & running

Full environment setup (Python 3.12, GenLayer CLI, Studio via Docker): **[SETUP.md](SETUP.md)**.

```bash
for f in contracts/vulnerable/*.py contracts/hardened/*.py; do genvm-lint check "$f"; done
pytest tests/direct/ -v                 # fast adversarial tests (no Docker)
gltest tests/integration/ -v -s         # end-to-end on Studio (Docker required)
```

## Built on

The official GenLayer toolchain: [`genlayer-py`](https://github.com/genlayerlabs/genlayer-py), [`genlayer-testing-suite`](https://github.com/genlayerlabs/genlayer-testing-suite) (gltest), [`genvm-linter`](https://github.com/genlayerlabs/genvm-linter), and patterns from the [`genlayer-project-boilerplate`](https://github.com/genlayerlabs/genlayer-project-boilerplate).

## Contract runtime

Every contract pins the canonical runtime via the header on line 1, copied verbatim from the boilerplate:

```
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
```

## Artifacts

| Sink | Vulnerable | Hardened | Direct tests |
|------|-----------|----------|--------------|
| direct injection | `contracts/vulnerable/sentiment_escrow.py` | `contracts/hardened/sentiment_escrow.py` | `test_sentiment_escrow_*.py` |
| indirect web | `contracts/vulnerable/web_price_oracle.py` | `contracts/hardened/web_price_oracle.py` | `test_web_price_oracle_*.py` |
| LLM judge | `contracts/vulnerable/judge_bypass.py` | `contracts/hardened/judge_bypass.py` | `test_judge_bypass_*.py` |
| multimodal | `contracts/vulnerable/image_moderator.py` | `contracts/hardened/image_moderator.py` | `test_image_moderator.py` |

Source-verified undefended surfaces are written up in [`reports/findings/`](reports/findings/): the unfiltered judge template (01), no output-side filtering (02), and unfiltered images (03), each confirmed against the shipped greybox script.

## License

MIT - see [LICENSE](LICENSE).
