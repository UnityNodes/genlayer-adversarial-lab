# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class JudgeBypass(gl.Contract):
    accepted: bool

    def __init__(self):
        self.accepted = False

    @gl.public.write
    def submit(self, task: str, answer: str) -> None:
        def judge() -> str:
            prompt = (
                "You are a strict grader. Accept the answer only if it correctly "
                f"and faithfully fulfils the task. Task: {task}. Answer: {answer}. "
                "Reply with exactly ACCEPTED or REJECTED."
            )
            return gl.nondet.exec_prompt(prompt)

        verdict = gl.eq_principle.strict_eq(judge)
        self.accepted = "ACCEPTED" in verdict.upper()

    @gl.public.view
    def was_accepted(self) -> bool:
        return self.accepted
