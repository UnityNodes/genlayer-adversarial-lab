# Finding 02: no output-side (model response) filtering in the default greybox script

- **Severity:** Medium (model-output abuse has no greybox coverage; must be handled contract-side)
- **Class:** Insufficient output handling (OWASP LLM01 / LLM05-style output trust)
- **Affected component:** default validator-side greybox script `genvm-llm-default.lua`, hooks `ExecPrompt` and `ExecPromptTemplate` -
  [L313-351](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua#L313-L351).

## Description

Both hooks filter (at most) the INPUT and then return the backend result directly via `just_in_backend(ctx, mapped, remaining_gen)`. No transform is applied to the model's RESPONSE. The greybox layer has no notion of output sanitisation.

## Reproduction

- Vulnerable target: [contracts/vulnerable/sentiment_escrow.py](../../contracts/vulnerable/sentiment_escrow.py) trusts a free-text verdict (`"YES" in out.upper()`).
- Direct test: [tests/direct/test_sentiment_escrow_vulnerable.py](../../tests/direct/test_sentiment_escrow_vulnerable.py) - a compromised model output releases escrow.
- Hardened counterpart proving the contract-side fix: [contracts/hardened/sentiment_escrow.py](../../contracts/hardened/sentiment_escrow.py) + [test](../../tests/direct/test_sentiment_escrow_hardened.py).

## Impact

Output-side attacks - schema hijacking, extra-field injection, model self-identification, control tokens in the answer - are invisible to the shipped greybox. A contract that trusts a free-text verdict or an unvalidated field inherits the full risk.

## Suggested mitigation

- Contract side (mandatory today): constrain output to a strict JSON schema, reject extra keys / wrong types, and make the money/state decision in deterministic Python from validated fields. Demonstrated by every hardened contract in this lab.
- Node/script side (optional hardening): add an output-side `filter_text` / schema check in the greybox script.

## References

- Surface audit: [00-surface-audit.md](00-surface-audit.md)
- ARCHITECTURE.md fact F6.
