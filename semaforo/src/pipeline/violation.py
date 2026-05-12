class ViolationDetector:

    def __init__(self, line_y):

        self.line_y = line_y
        self.total_violations = 0

    def check_violation(self, vehicles, light_state):

        violations = []

        if light_state != "RED":
            return violations

        for (x, y, w, h) in vehicles:

            center_y = y + h // 2

            if center_y > self.line_y:

                self.total_violations += 1

                violations.append((x, y, w, h))

        return violations