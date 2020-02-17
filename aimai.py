from api import get_access_token, anaphoric, parse_sentences,parse
from parsing import Parser
from lex import lexical
import sys


def compiler(parsed):
    results = []
    for p in parsed:
        results.append(p.conv())

    return "\n".join(results)


if __name__ == '__main__':
    filepath = sys.argv[1]
    with open(filepath, 'r') as f:
        text = f.read()

    access_token = get_access_token()
    data, users = anaphoric(access_token, text)
    string_parsed, expressions = parse_sentences(data)
    r = lexical(parse(access_token, string_parsed))
    parser = Parser(r, expressions, users)
    parsed = parser.parse()
    compiled = compiler(parsed)

    exec(compiled)
