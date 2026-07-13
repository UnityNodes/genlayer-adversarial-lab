# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class WebPriceOracle(gl.Contract):
    price: u256

    def __init__(self):
        self.price = 0

    @gl.public.write
    def settle(self, url: str) -> None:
        def extract() -> str:
            page = gl.nondet.web.render(url, mode="text")
            prompt = (
                "Read the web content below and return the settlement price as a "
                f"plain integer, digits only.\nWeb content:\n{page}"
            )
            return gl.nondet.exec_prompt(prompt)

        raw = gl.eq_principle.strict_eq(extract)
        self.price = int(raw)

    @gl.public.view
    def get_price(self) -> int:
        return self.price
