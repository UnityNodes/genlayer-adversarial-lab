# Finding 03: images are not filtered by the default greybox script

- **Severity:** Medium (undefended multimodal injection channel by default)
- **Class:** Multimodal prompt injection (OWASP LLM01)
- **Affected component:** default validator-side greybox script `genvm-llm-default.lua`, hook `ExecPrompt` -
  [L313-338](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua#L313-L338).

## Description

`ExecPrompt` filters only `args.prompt` (`filter_text`). It never calls `filter_image` and never touches `args.images`. The built-in image filters (`Denoise`, `GaussianNoise`, `Unsharpen`, `JPEG`) exist in the runtime but are not wired into the shipped default script, so images pass to the model unmodified by default.

## Reproduction

- Vulnerable target: [contracts/vulnerable/image_moderator.py](../../contracts/vulnerable/image_moderator.py) trusts the model verdict on an image.
- Direct test: [tests/direct/test_image_moderator.py](../../tests/direct/test_image_moderator.py) - `test_vulnerable_image_injection_flips_moderation` (Direct mode accepts `bytes` and `exec_prompt(images=[...])`; the mock simulates a model swayed by text rendered inside the image).

## Impact

Text rendered inside an image (an instruction painted into the pixels) reaches the model with no normalisation. A moderation or verification contract that trusts the model's image verdict is exposed to text-in-image injection with no default greybox defense.

## Suggested mitigation

- Node/script side: wire the built-in `ImageFilter` set into `ExecPrompt` for `args.images`.
- Contract side (available today): validate the verdict against a strict allow-list and instruct the model to ignore in-image text. See [contracts/hardened/image_moderator.py](../../contracts/hardened/image_moderator.py).

## References

- Surface audit: [00-surface-audit.md](00-surface-audit.md)
- ARCHITECTURE.md facts F2, F6.
