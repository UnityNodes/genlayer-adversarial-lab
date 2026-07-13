# Finding 01: equivalence-principle judge template is not greybox-filtered

- **Severity:** Medium (defense-in-depth gap; enables obfuscated injection into the judge)
- **Class:** Prompt injection / input sanitisation gap (OWASP LLM01)
- **Affected component:** default validator-side greybox script `genvm-llm-default.lua`, hook `ExecPromptTemplate` -
  [L340-351](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua#L340-L351)
  (compare `ExecPrompt` at [L313-338](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua#L313-L338)).

## Description

`ExecPrompt` normalises its input with `filter_text(args.prompt, {"NFKC","RmZeroWidth","NormalizeWS"})` before sending it to the backend. `ExecPromptTemplate` - the hook that renders the equivalence-principle judge template consumed by `gl.eq_principle.prompt_comparative` and `prompt_non_comparative` - applies no `filter_text` at all. The judge criteria string is therefore exempt from the same-node text normalisation that protects a normal prompt.

## Reproduction

- Vulnerable target: [contracts/vulnerable/judge_bypass.py](../../contracts/vulnerable/judge_bypass.py)
- Direct test: [tests/direct/test_judge_bypass_vulnerable.py](../../tests/direct/test_judge_bypass_vulnerable.py) - `test_criteria_injection_forces_accept`.

The Direct test demonstrates the class leader-side (attacker `task` text concatenated into the grader prompt flips the verdict), because the pure equivalence-principle judging runs validator-side and is not exercised in leader-only Direct mode. Note that the reproduction contract uses `gl.eq_principle.strict_eq` + `exec_prompt` (the FILTERED `ExecPrompt` path), so it demonstrates the general injection class rather than the specific template gap; the unfiltered-`ExecPromptTemplate` defect itself is established by the source audit (finding 00), which is the direct evidence.

## Impact

Homoglyph, zero-width, and whitespace obfuscation that the default filter neutralises inside a normal prompt survives inside the judge criteria. An attacker who can influence the criteria string can smuggle instructions past the judge that a filtered prompt would strip.

## Suggested mitigation

- Node/script side: pass the rendered template through `filter_text` in `ExecPromptTemplate`, matching `ExecPrompt`.
- Contract side (available today): keep the equivalence criteria a fixed contract constant and pass user text only as delimited data; judge via a strict schema. See [contracts/hardened/judge_bypass.py](../../contracts/hardened/judge_bypass.py).

## References

- Surface audit: [00-surface-audit.md](00-surface-audit.md)
- ARCHITECTURE.md facts F5, F6.
