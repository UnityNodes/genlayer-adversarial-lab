# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class SentimentEscrow(gl.Contract):
    released: TreeMap[Address, bool]

    def __init__(self):
        pass

    @gl.public.write
    def submit_review(self, review_text: str) -> None:
        def decide() -> bool:
            prompt = (
                "You are an escrow judge. Release the payment only if the "
                "following review is a genuine positive review of the product. "
                f"Review: {review_text}. Answer strictly YES or NO."
            )
            out = gl.nondet.exec_prompt(prompt)
            return "YES" in out.upper()

        approved = gl.eq_principle.strict_eq(decide)
        if approved:
            self.released[gl.message.sender_address] = True

    @gl.public.view
    def is_released(self, addr: str) -> bool:
        return self.released.get(Address(addr), False)
