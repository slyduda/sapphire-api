from dotenv import dotenv_values

from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(dotenv_values(".env").get('APP_SECRET'))


def create_token(payload, salt=None):
    pass


def load_token(token, salt=None, max_age=None):
    try:
        return serializer.loads(token, salt=salt, max_age=max_age)
    except:
        return None