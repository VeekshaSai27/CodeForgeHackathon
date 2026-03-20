def detect_exaggeration(claimed_level, proficiency):
    if claimed_level == "expert" and proficiency < 0.4:
        return True
    return False