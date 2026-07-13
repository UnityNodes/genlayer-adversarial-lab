# GLAdversary: a runnable, source-verified security analysis of prompt-injection surfaces in GenLayer Intelligent Contracts

## Abstract

GenLayer Intelligent Contracts can call LLMs and fetch the web without oracles, which
turns two ordinary operations, `gl.nondet.exec_prompt` and `gl.nondet.web`, into
untrusted-data sinks. This analysis maps those sinks, demonstrates each with a runnable
vulnerable contract and its hardened counterpart, verifies the shipped greybox behavior
against GenVM source, and measures a set of greybox transforms against an attack corpus (transform-level; the on-node attack-success-rate ablation is Phase 2).
The central result, verified against source and demonstrated in code: consensus only
catches non-deterministic divergence between validators, so a prompt injection that flips
every node the same way passes consensus untouched. Integrity must therefore live in
deterministic contract logic, not in the equivalence principle. Everything here is
runnable and reproducible (26 Direct-mode tests, studionet and testnet deployments), which
is what distinguishes it from descriptive analyses.

Repository: <https://github.com/UnityNodes/genlayer-adversarial-lab>

## 1. Method

- Source-verify the GenVM greybox model (the default validator-side Lua transform and the
  Rust filter set) and record the facts the lab depends on (see
  [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md), facts F1 to F6).
- For each untrusted-data sink, build a naive contract that trusts model output and a
  hardened contract that does not, and prove the difference with Direct-mode tests where
  the LLM and web are mocked (so the design-level flaw is shown honestly, independent of
  any specific model).
- Confirm the end-to-end path on a real node (studionet, no local Docker) and deploy the
  flagship contracts to both testnets (Asimov and Bradbury).
- Implement and measure greybox defenses against an attack corpus, and report which work.

## 2. Attack taxonomy: four sinks, each runnable

| Sink | Vulnerable contract | Class |
|------|---------------------|-------|
| user argument to `exec_prompt` | [`sentiment_escrow`](../contracts/vulnerable/sentiment_escrow.py) | direct prompt injection |
| web content to `exec_prompt` | [`web_price_oracle`](../contracts/vulnerable/web_price_oracle.py) | indirect (second-order) injection |
| attacker text to the LLM judge | [`judge_bypass`](../contracts/vulnerable/judge_bypass.py) | judge / equivalence-criteria injection |
| image bytes to `exec_prompt` | [`image_moderator`](../contracts/vulnerable/image_moderator.py) | multimodal injection |

Each sink has a paired hardened contract and Direct-mode tests
([tests/direct/](../tests/direct/)). The indirect-web class is the most severe: every
validator renders the same poisoned page, so a wrong value is identical on all nodes and
becomes an agreed majority that consensus cannot reject.

## 3. The core result

`strict_eq` compares the leader and validator results with no LLM; if a compromised or
injected model returns the same value on every node, the results match and consensus
agrees. The vulnerable `sentiment_escrow` test encodes exactly this: a negative review
with an injected instruction releases escrow, and the state change is the proof. Consensus
is a defense against non-determinism, not against a deterministic lie. The reliable fix is
deterministic grounding: the hardened contracts force a strict JSON schema, reject
off-schema output, and make the money or state decision in Python from validated fields,
never from a free-text verdict.

## 4. Source-verified undefended surfaces

Read against `genvm-llm-default.lua` (pinned permalinks in
[reports/findings/00-surface-audit.md](findings/00-surface-audit.md)):

1. The equivalence-principle judge template (`ExecPromptTemplate`) is not passed through
   `filter_text`, unlike `ExecPrompt` ([finding 01](findings/01-judge-template-unfiltered.md)).
2. There is no output-side filtering; both hooks filter input only
   ([finding 02](findings/02-no-output-side-filtering.md)).
3. `ExecPrompt` filters only `args.prompt`, never `args.images`
   ([finding 03](findings/03-images-unfiltered.md)).

## 5. Greybox defenses: implemented and measured

The [`greybox/`](../greybox/) directory implements advanced validator-side techniques with
a tested reference ([transforms.py](../greybox/transforms.py),
[tests](../tests/direct/test_greybox_transforms.py)) and a node-deployable Lua script that
also closes the three surfaces above. Measured results on the corpus:

- Cross-script confusables normalization neutralizes the Cyrillic homoglyph payload that
  the default NFKC leaves untouched.
- The perplexity proxy flags the out-of-vocabulary adversarial suffix but not the
  real-word one; robust coverage needs language-model perplexity.
- Normalization strips zero-width payloads (matches the shipped default).

Bottom line from the defender side: greybox is input and output hygiene that hardens the
obfuscation, multimodal, and template surfaces, but it does not stop a fluent injection.
That reinforces the thesis: integrity belongs in contract logic.

## 6. Corrections surfaced by building it

Because the lab is runnable, it corrected two claims that are easy to assume:

- **NFKC does not neutralize cross-script confusables.** Homoglyphs like Cyrillic `о`
  (U+043E) survive the shipped default; only an explicit confusables map removes them
  (verified in `test_greybox_transforms.py`). ARCHITECTURE fact F2 was updated.
- **Lexical perplexity cannot see real-word adversarial suffixes.** A suffix built from
  ordinary words in a nonsense order has 0% out-of-vocabulary tokens, so a Zipf-based
  proxy passes it. This bounds what a cheap perplexity filter can do.

Two tooling findings also came out of the empirical work: in the current Direct-mode SDK
build, `run_validator()` cannot re-run a `strict_eq` validator (its sandbox result fails to
decode), so attack success is asserted on contract state instead; and the latest released
Python client (`genlayer-py` 0.18) cannot decode the current testnet consensus contract, so
testnet deploys go through the newer `genlayer` CLI (documented in
[deploy/NOTES.md](../deploy/NOTES.md)).

## 7. Evidence

- 26 Direct-mode tests green; 8 contracts pass `genvm-lint check`.
- End-to-end on studionet (deploy plus a real nondet consensus write).
- Testnet deployments on both Asimov and Bradbury, verified on-chain with `genlayer
  schema` (addresses and explorer links in [deploy/NOTES.md](../deploy/NOTES.md)).

## 8. Roadmap

- Phase 2: on-node greybox ablation, measuring attack-success-rate ON versus OFF per
  technique on a live validator with a model backend.
- Phase 3: fold the ablation results and the confirmed surfaces into a full write-up and a
  defense-pattern matrix for contract authors.

## 9. Conclusion

The equivalence principle secures against non-deterministic disagreement, not against a
deterministic injection that every validator shares. Contract authors must treat model and
web output as untrusted, constrain it to a strict schema, and make the decision in
deterministic code; node operators can harden the perimeter with greybox, including the
confusables, template, output, and image steps this lab adds, but cannot substitute for
contract-side integrity. The lab is the runnable evidence for that claim.
