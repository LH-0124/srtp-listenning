class PatientState:
    def __init__(self):
        # 初始参数：正常语速，背景音较小
        self.speed = 1.0 
        self.snr = 20    # dB
        self.history = []

    def adjust(self, is_correct: bool):
        """
        自适应核心逻辑：正确就加难，错误就变易
        """
        self.history.append(is_correct)
        
        prev_speed = self.speed
        prev_snr = self.snr
        msg = ""

        if is_correct:
            # 加大难度：语速变快(up to 2.0)，噪音变大(SNR变小 down to 0)
            self.speed = min(self.speed + 0.1, 2.0)
            self.snr = max(self.snr - 2, 0)
            msg = "回答正确，难度提升"
        else:
            # 降低难度：语速变慢(down to 0.8)，噪音变小(SNR变大 up to 30)
            self.speed = max(self.speed - 0.2, 0.8)
            self.snr = min(self.snr + 3, 30)
            msg = "回答错误，难度降低"
            
        return {
            "correct": is_correct,
            "msg": msg,
            "new_params": {"speed": self.speed, "snr": self.snr}
        }