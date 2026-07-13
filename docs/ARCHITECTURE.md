# Architecture & Technical Foundation

This document records the source-verified facts about GenLayer's security model that the lab is built on, the attack taxonomy, the defense layers, and the testing methodology.

## 1. GenVM security model (verified against source)

| # | Fact | Consequence |
|---|------|-------------|
| F1 | **Greyboxing is a validator-side Lua 5.4 script** in the GenVM LLM Module (`genvm-llm-default.lua`, hook `ExecPrompt(ctx, args, remaining_gen)`) - not a contract feature and not a config flag. | Turning it on/off is a node-operator action (swap `lua_script_path`), never a contract change. |
| F2 | The shipped default transform is literally `filter_text(args.prompt, {"NFKC","RmZeroWidth","NormalizeWS"})` + empty-prompt reject. The full built-in filter set is `TextFilter{NFC,NFKC,NormalizeWS,RmZeroWidth}` and `ImageFilter{Denoise,Unsharpen,GuassianNoise,JPEG}` (names verbatim from `filters.rs`, including the upstream `Guassian` spelling). | Zero-width and whitespace tricks, and compatibility homoglyphs, are neutralized out of the box. But NFKC does **not** map cross-script confusables (for example Cyrillic `о` U+043E to Latin `o`), so those survive the default (verified empirically; see `greybox/`). Paraphrase / retokenize / perplexity are **not** shipped filters - they must be written in Lua. |
| F3 | Four defense layers exist: greybox (input transform) → equivalence-principle choice (`strict_eq` / `prompt_comparative` / `prompt_non_comparative`) → consensus economics (appeal/slash) → deterministic Python grounding. | Each attack is mapped to the layer that actually stops it, on a matrix - not a single silver bullet. |
| F4 | **Consensus only catches non-deterministic divergence between validators.** A deterministic jailbreak that flips every node the same way passes consensus. | Integrity must live in contract logic. Hardened variants add deterministic guards. |
| F5 | `strict_eq` compares leader vs validator results with **no LLM**; `prompt_comparative` and `prompt_non_comparative` feed strings **through an LLM judge**. | The equivalence criteria string is itself an injection surface (see `judge_bypass`). |
| F6 | The default `ExecPrompt` filters the **input** prompt only; the equivalence-principle judge template (`ExecPromptTemplate`) is **not** passed through `filter_text`, and there is **no output-side filtering**. | Judge-template injection and model-output abuse (schema hijack, self-identification) have no greybox coverage - contract-side validation is mandatory. |

## 2. Attack taxonomy → target contracts

Intelligent Contracts reach non-determinism via `gl.nondet.exec_prompt(...)` and `gl.nondet.web.get/render(...)`, each wrapped in an equivalence principle. The untrusted-data sinks:

- **Direct prompt injection** - a user argument is concatenated into the prompt. Target: `sentiment_escrow`. A crafted argument flips the model's verdict; because the result is the same on every node, `strict_eq` agrees and the attack succeeds.
- **Indirect / second-order injection** - content fetched from the web (no oracle sanitizes it) is fed to the model. Target: `web_price_oracle`. The attacker controls the page (hidden HTML comment, white-on-white text, meta/alt). Every validator ingests the same poisoned content, so the wrong value can become an agreed majority - the highest-severity class.
- **Equivalence-principle criteria injection** - attacker text flows into the `principle`/`criteria` string that the judge LLM reads. Target: `judge_bypass`. The judge's own instructions are overridden.

Additional classes catalogued in the corpus (`attacks/`): homoglyph/zero-width obfuscation (neutralized by F2 defaults), high-perplexity adversarial suffixes, output-schema hijacking, and consensus-splitting (borderline inputs engineered to make diverse validators disagree → the tx reaches an `Undetermined` state; a liveness/griefing vector with no greybox fix).

## 3. Defense patterns (hardened contracts)

- **Strict output schema** - force `response_format` JSON with a fixed shape; reject extra keys / malformed output.
- **Deterministic grounding** - make the money/state decision in Python from extracted stable fields; never trust a free-text verdict or an out-of-band value.
- **Delimit untrusted data** - wrap user/web content in tags and instruct the model to treat it as data, never as instructions.
- **Independent judging** - use `prompt_non_comparative` so validators judge integrity themselves rather than trusting the leader.
- **Fixed criteria** - keep equivalence criteria a contract constant; pass user text only as delimited data.

## 4. Testing methodology

Two modes, from the GenLayer testing suite (gltest):

- **Direct mode** (`tests/direct/`, in-memory, no Docker). Cheatcodes `mock_llm(regex, output)`, `mock_web(regex, body)`, `expect_revert(...)`, `run_validator() -> bool`. Because the LLM is **mocked**, Direct-mode tests prove **design-level** vulnerabilities honestly: they simulate a compromised model output and show that the vulnerable contract performs the malicious action while the hardened one blocks it deterministically. `run_validator()` shows whether consensus would catch it (for `strict_eq` on a same-for-all bool, it does not - encoding F4).
- **Integration mode** (`tests/integration/`, Studio/localnet, real multi-validator consensus) for the end-to-end path.

### The "attack caught?" oracle, three levels
1. **Contract-level** - hardened rejects (`expect_revert`) / state unchanged.
2. **Consensus-level** - `run_validator() == False` → `Undetermined`. We distinguish *wrong-but-agreed* (worst - consensus does not catch it) from *Undetermined/griefing* (liveness/DoS).
3. **Greybox-level** - measured empirically on a real node (roadmap), attack-success-rate ON vs OFF.

## 5. Roadmap

- **Phase 1 (current) - GLAdversary:** the three+ target contracts, hardened variants, Direct-mode adversarial tests, and Studio end-to-end.
- **Phase 2 - GreyboxBench:** custom validator-side Lua greybox scripts (paraphrase / perplexity / retokenize) on a real node; measure attack-success-rate with per-technique ablation. This is the empirical gap no existing GenLayer work fills.
- **Phase 3 - Report:** synthesize the empirical results and the confirmed undefended surfaces (F6) into a written security analysis.

Explicit non-goals for now: a full consensus-economics simulator (appeal/slash parameters still being finalized on current testnet), and a heavyweight benchmark framework.

## 6. Sources

- GenVM: `github.com/genlayerlabs/genvm` - `modules/install/config/genvm-llm-default.lua`, `modules/install/config/genvm-module-llm.yaml`, `modules/implementation/src/scripting/ctx/filters.rs`, `doc/website/src/impl-spec/03-greyboxing/`.
- SDK: `sdk.genlayer.com/main/_static/ai/api.txt`.
- Testing & patterns: `github.com/genlayerlabs/genlayer-testing-suite`, `github.com/genlayerlabs/genlayer-project-boilerplate`.
- Background: OWASP LLM Top 10 (2025); Jain et al., *Baseline Defenses for Adversarial Attacks Against Aligned LLMs* (arXiv:2309.00614).
