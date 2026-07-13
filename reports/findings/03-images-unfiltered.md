# Finding 03: images are not filtered by the default greybox script

- **Severity:** Medium (undefended multimodal injection channel by default)
- **Class:** Multimodal prompt injection (OWASP LLM01)
- **Affected component:** default validator-side greybox script `genvm-llm-default.lua`, hook `ExecPrompt` -
  [L313-338](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua#L313-L338).

## Description

`ExecPrompt` filters only `args.prompt` (`filter_text`). It never calls `filter_image` and never touches `args.images`. The built-in image filters are defined in the runtime as the `ImageFilter` enum (`Denoise`, `Unsharpen`, `GuassianNoise` [sic, as spelled in source], `JPEG`; [filters.rs L10-15](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/implementation/src/scripting/ctx/filters.rs#L10-L15)) but are not wired into the shipped default script, so images pass to the model unmodified by default.

## Reproduction

- Vulnerable target: [contracts/vulnerable/image_moderator.py](../../contracts/vulnerable/image_moderator.py) trusts the model verdict on an image.
- Direct test: [tests/direct/test_image_moderator.py](../../tests/direct/test_image_moderator.py) - `test_vulnerable_trusts_model_verdict` proves the contract stores whatever verdict the model returns (Direct mode accepts `bytes` and `exec_prompt(images=[...])`). The image is opaque to the LLM mock, so Direct mode cannot drive an image-content flip; the unfiltered-image channel itself is established by the source audit above, not by this test.

## Impact

Text rendered inside an image (an instruction painted into the pixels) reaches the model with no normalisation. A moderation or verification contract that trusts the model's image verdict is exposed to text-in-image injection with no default greybox defense.

## Suggested mitigation

- Node/script side: apply an image control to `args.images` in `ExecPrompt`. Note the built-in `ImageFilter` set (`Denoise`, `Unsharpen`, `GuassianNoise`, `JPEG`) targets pixel-level adversarial perturbation, not rendered text, so text-in-image injection needs an OCR or vision-model check rather than these magnitude filters alone.
- Contract side (available today): validate the verdict against a strict allow-list and instruct the model to ignore in-image text. See [contracts/hardened/image_moderator.py](../../contracts/hardened/image_moderator.py).

## References

- Surface audit: [00-surface-audit.md](00-surface-audit.md)
- Image filter set in source: [filters.rs L10-15](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/implementation/src/scripting/ctx/filters.rs#L10-L15).
- docs/ARCHITECTURE.md facts F2, F6.
