from common.models import User, Session

def validate_password(username, password):
    try:
        user = User.get(User.username == username)
    except User.DoesNotExist:
        return False

    return user.validate(password)

def validate_token(token):
    return Session.validate(token)
