class SpeechClassifier:
    """
    Backend only validates voice flag from browser.
    Temporal validation is handled in websocket.
    """
    def __init__(self):
        pass

    def process(self, voice_flag: bool):
        return {
            "voice_detected": bool(voice_flag)
        }