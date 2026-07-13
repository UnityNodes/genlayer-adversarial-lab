# Surface audit: undefended greybox channels (source-verified)

**Method.** Read the shipped default validator-side greybox script and confirm, against source, which channels the default `filter_text` transform does and does not cover. This audit is the basis for the bug-report writeups (01-03) and gates the `image_moderator` target.

**Source (pinned).** `genvm-llm-default.lua` at genvm `main` @ `abb71bf891695b737e6a4f5211f4740a3b25543d`:
<https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua>

The two relevant hooks, verbatim:

- `ExecPrompt(ctx, args, remaining_gen)` (L313-338): filters the input prompt
  ```lua
  args.prompt = lib.rs.filter_text(args.prompt, { "NFKC", "RmZeroWidth", "NormalizeWS" })
  ```
  then rejects empty prompts and forwards `llm.exec_prompt_transform(args)` to the backend.
- `ExecPromptTemplate(ctx, args, remaining_gen)` (L340-351): NO `filter_text` call. It goes straight to `llm.exec_prompt_template_transform(args)` and `just_in_backend(...)`.

## Claim 1 - equivalence-principle judge template is unfiltered - CONFIRMED

`ExecPrompt` passes `args.prompt` through `filter_text`; `ExecPromptTemplate` (the hook that renders the equivalence-principle judge template used by `prompt_comparative` / `prompt_non_comparative`) applies no text filter at all.

- Evidence: [L313-338](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua#L313-L338) vs [L340-351](https://github.com/genlayerlabs/genvm/blob/abb71bf891695b737e6a4f5211f4740a3b25543d/modules/install/config/genvm-llm-default.lua#L340-L351).
- Consequence: homoglyph / zero-width / whitespace tricks that are neutralised inside a normal prompt are NOT neutralised inside the judge criteria string. Contract-side handling of the criteria is mandatory. Feeds finding 01.

## Claim 2 - no output-side (response) filtering - CONFIRMED

Both hooks filter only the INPUT (`ExecPrompt` filters `args.prompt`; `ExecPromptTemplate` filters nothing) and return the backend result directly via `just_in_backend(...)`. There is no transform applied to the model's response.

- Evidence: neither hook post-processes the return value; both end in `return just_in_backend(ctx, mapped, remaining_gen)`.
- Consequence: model-output abuse (schema hijack, self-identification, control tokens in the answer) has no greybox coverage. Deterministic contract-side output validation is mandatory. Feeds finding 02, and is exactly what the hardened contracts enforce (strict JSON schema + Python guard).

## Claim 3 - images are unfiltered by the default script - CONFIRMED

`ExecPrompt` filters only `args.prompt`. It never calls `filter_image` and never touches `args.images`. The built-in image filters (`Denoise`, `GuassianNoise`, `Unsharpen`, `JPEG`) exist but are NOT wired into the shipped default script.

- Evidence: the only filter call in `ExecPrompt` is `filter_text(args.prompt, ...)`; there is no `filter_image` anywhere in the default script.
- Consequence: text rendered inside an image reaches the model unmodified by default - an undefended multimodal injection channel. Gates the `image_moderator` target (GO). Feeds finding 03.

## Outcome

All three claims CONFIRMED against source. Downstream:
- `image_moderator` target: GO (Task 1.7).
- Bug-report writeups: 01 (judge-template unfiltered), 02 (no output-side filtering), 03 (images unfiltered).
