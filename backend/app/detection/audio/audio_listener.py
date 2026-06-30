class AudioListener:
    """
    Browser-based audio interface.
    Backend does not capture microphone.
    """
    def __init__(self):
        pass

    def get_status(self, voice_flag: bool):
        return {
            "voice_detected": bool(voice_flag)
        }