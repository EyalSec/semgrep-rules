import random
import secrets
import string


def reset_token(n=12):
    # ruleid: random-for-secret-value
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def make_reset_token(n=32):
    # ok: random-for-secret-value
    return secrets.token_urlsafe(n)


def create_user(email):
    # ruleid: random-for-secret-value
    temp_password = "".join(random.choices(string.ascii_letters, k=10))
    # ruleid: random-for-secret-value
    otp = random.randint(100000, 999999)
    # ok: random-for-secret-value
    avatar_color = random.choice(["red", "green", "blue"])
    return temp_password, otp, avatar_color


def shuffle_deck(cards):
    # ok: random-for-secret-value
    return random.sample(cards, len(cards))
