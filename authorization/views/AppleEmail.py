import time

import jwt
from pip._vendor import requests

apple_auth_url = "https://appleid.apple.com/auth/token"
key_id = "KU8QV63Q7V"
team_id = "XQWWX24964"
client_id = "com.ra.houzes-ios"

private_key = b'-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg21mdVNhE9lYGRx5Q\nYrSTCa3EOru90NPIg07efZi2cCagCgYIKoZIzj0DAQehRANCAASplaS7y6V615hW\nKO40YQGS/Eh4qufM+RMN0VaVZ9EXGW4OY3aNv3mU2f4zC/ewmTdAGSOFvJtR1za/\nV6267Nx6\n-----END PRIVATE KEY-----'
issued_timestamp = time.time()
expiration_timestamp = issued_timestamp + 180


def get_email(code):
    try:
        client_secret = jwt.encode(
            {
                'iss': team_id,
                'iat': issued_timestamp,
                'exp': expiration_timestamp,
                'aud': 'https://appleid.apple.com',
                'sub': client_id
            },
            private_key,
            algorithm='ES256',
            headers={'kid': key_id}).decode("utf-8")

        post_headers = {'content-type': "application/x-www-form-urlencoded"}
        post_body = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
        }

        post_res = requests.post(apple_auth_url, data=post_body, headers=post_headers)
        post_json = post_res.json()
        id_token = post_json.get('id_token', None)
        if id_token:
            decoded = jwt.decode(id_token, '', verify=False)
            print((decoded['sub']) if 'sub' in decoded else None)
            return ((decoded['email']) if 'email' in decoded else None)
    except Exception as ex:
        print("-------------------token error---------------")
        print(str(ex))
    return None


import random

domains = ["hotmail.com", "gmail.com", "aol.com", "mail.com", "mail.kz", "yahoo.com"]
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']


def get_one_random_domain(domains):
    return random.choice(domains)


def get_one_random_name(letters):
    return ''.join(random.choice(letters) for i in range(20))


def generate_random_emails():
    return get_one_random_name(letters) + '@houzes.com'
