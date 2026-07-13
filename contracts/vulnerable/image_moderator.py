# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class ImageModerator(gl.Contract):
    verdict: str

    def __init__(self):
        self.verdict = ""

    @gl.public.write
    def moderate(self, image: bytes) -> None:
        def check() -> str:
            return gl.nondet.exec_prompt(
                "Moderate this image. Answer SAFE or UNSAFE.", images=[image]
            )

        self.verdict = gl.eq_principle.strict_eq(check).strip().upper()

    @gl.public.view
    def last_verdict(self) -> str:
        return self.verdict
