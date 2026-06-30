# """
# Aggregates multiple violations into a final risk score
# """


# class RiskScorer:
#     def calculate_risk(self, violations):

#         weights = {
#             "multiple_faces": 40,
#             "no_face": 35,
#             "looking_away": 25,
#             "phone_detected": 50,
#         }

#         total_score = 0

#         for event, confidence in violations.items():
#             weight = weights.get(event, 20)
#             total_score += weight * confidence

#         return min(total_score, 100)


"""
Improved Risk Scoring System
Prevents duplicate scoring and stabilizes final risk calculation
"""


class RiskScorer:
    def __init__(self):
        # Track already counted violations
        self.recorded_events = set()

        # Weights for each violation
        self.weights = {
            "multiple_faces": 40,
            "no_face": 35,
            "looking_away": 25,
            "phone_detected": 50,
        }

    def calculate_risk(self, violations):
        total_score = 0

        for event, confidence in violations.items():

            # 🔥 Prevent duplicate counting
            if event in self.recorded_events:
                continue

            weight = self.weights.get(event, 20)

            # Normalize confidence (0–1 scale)
            normalized_conf = confidence / 100

            total_score += weight * normalized_conf

            # Mark event as counted
            self.recorded_events.add(event)

        return min(int(total_score), 100)

    def reset(self):
        """
        Reset for new session
        """
        self.recorded_events.clear()