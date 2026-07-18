from database import deduct_usage, get_remaining_count


def check_and_deduct(user_id: int) -> tuple[bool, str]:
    remaining = get_remaining_count(user_id)
    if remaining <= 0:
        return False, "免费次数已用完，请升级会员"
    deduct_usage(user_id)
    return True, ""


def get_remaining(user_id: int) -> int:
    return get_remaining_count(user_id)
