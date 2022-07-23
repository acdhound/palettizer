class UserStep:
    PICTURE = "PICTURE"
    PALETTE = "PALETTE"
    N_COLORS = "N_COLORS"
    PROCESSING = "PROCESSING"
    RESULT = "RESULT"
    steps: list[str] = [PICTURE, PALETTE, N_COLORS, PROCESSING, RESULT]

    current_step: int = 0

    def __init__(self, step: str = PICTURE):
        if step not in self.steps:
            self.current_step = 0
        self.current_step = self.steps.index(step)

    def next(self):
        if self.current_step >= len(self.steps) - 1:
            return self
        return UserStep(self.steps[self.current_step + 1])

    def prev(self):
        if self.current_step <= 0:
            return self
        return UserStep(self.steps[self.current_step + 1])
