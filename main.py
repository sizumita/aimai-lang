import json
import requests
from pprint import pprint
import re
from lex import *
from parsing import Parser
import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DEVELOPER_API_BASE_URL = "https://api.ce-cotoha.com/api/dev/"
ACCESS_TOKEN_PUBLISH_URL = "https://api.ce-cotoha.com/v1/oauth/accesstokens"

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
testcase = "太郎は1を持っています。"
expressions = []
Variables = {}


class Null:
    """Noneと見分けるためのclass"""
    pass


def get_access_token():
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "grantType": "client_credentials",
        "clientId": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
    }

    data = json.dumps(data).encode()

    response = requests.post(ACCESS_TOKEN_PUBLISH_URL, data=data, headers=headers)
    return response.json()['access_token']


def anaphoric(access_token, text):
    """
    代名詞を名詞に変えて返却
    returns: トークン一覧, 変数名となる人名一覧
    """
    url = DEVELOPER_API_BASE_URL + "nlp/v1/coreference"
    data = {
        "document": text,
    }
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json;charset=UTF-8",
    }
    users = []
    data = json.dumps(data).encode()
    response = requests.post(url, data=data, headers=headers)
    j = response.json()
    datas = j['result']['coreference']
    tokens = j['result']['tokens'][0]
    for content in datas:
        referents = content['referents']
        #  花子　と　花子さん　の両方が引っかかってしまう場合がある
        if referents[0]['token_id_from'] != referents[0]['token_id_to']:
            continue

        real_name = referents.pop(0)['form']
        users.append(real_name)
        for lie in referents:
            tokens[lie['token_id_from']] = real_name

    return tokens, users


def parse_sentences(tokens):
    text = ''.join(tokens).replace('\n', '')
    text = text.replace(':', '。')  # if, while
    result = ""
    for s in text.split('。'):
        match = re.match('もし(.+)ならば', s)
        if match:
            exp = match.groups()[0]
            expressions.append(exp)
            s = s.replace(exp, '条件式' + str(len(expressions)))
        elif s == 'NHKを、ぶっ壊す。':
            s = '壊す'

        result += f'{s}。'

    return text


def parse(access_token, text):
    url = DEVELOPER_API_BASE_URL + "nlp/v1/parse"
    data = {
        "sentence": text,
    }
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json;charset=UTF-8",
    }
    data = json.dumps(data).encode()
    response = requests.post(url, data=data, headers=headers)
    j = response.json()

    return j['result']


if __name__ == '__main__':
    access_token = get_access_token()
    data, users = anaphoric(access_token, '太郎くんは花子さんを持ちました。')
    # data, users = anaphoric(access_token, '山田くんは５を持ちました。\n山田くんを表示する。')
    r = lexical(parse(access_token, parse_sentences(data)))
    parser = Parser(r, expressions, users)
    parser.parse()
