from lex import *
import re
ID_compile = re.compile(r'^(.+)さん|くん|ちゃん|様|$')


class Int:
    def __init__(self, value):
        self.value = value


class Str:
    def __init__(self, value):
        self.value = value


class List:
    def __init__(self, values):
        self.values = values


class ID:
    def __init__(self, value):
        self.value = value


class Assign:
    """代入式"""
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Function:
    def __init__(self, func, value):
        self.func = func
        self.value = value


def get_all_child_phrases(phrase):
    results = {}
    for i, child in phrase.child_phrases.items():
        results[i] = child
        results.update(get_all_child_phrases(child))

    return results


def get_all_tokens(phrase):
    """フレーズとその子フレーズのトークンを全て取得します。
    return: {id: token}
    """
    phrases = get_all_child_phrases(phrase)
    phrases[phrase.id] = phrase
    tokens = {}
    for i, p in phrases.items():
        tokens[p.main_token.id] = p.main_token
        tokens.update(p.sub_tokens)
    return tokens


def join_tokens(tokens):
    result = ""
    for token in tokens:
        result += token.form

    return result


class Parser:
    def __init__(self, lexed, expressions, variables):
        self.lexed = lexed
        self.exp_list = expressions
        self.var_list = variables

    def exp(self, value):
        joined = join_tokens(value)
        if re.match(r'^[0-9]+$', joined):
            return Int(joined)
        elif re.match(r'^".+"$', joined):
            return Str(joined[1:-1])
        elif re.match(r'^\[.+\]$', joined):
            return self.list(re.match(r'^\[(.+)]$', joined).groups()[0])
        elif ID_compile.match(joined):
            return ID(ID_compile.match(joined).groups()[0])

        return ''

    def assign(self, value):
        phrase = value.get_links('object')[0]
        tokens = get_all_tokens(phrase)
        sorted_tokens = sorted(tokens.items(), key=lambda x: x[0])
        result_tokens = []

        for token in sorted_tokens:
            if 'を' == token[1].form:
                continue
            result_tokens.append(token[1])

        exp = self.exp(result_tokens)

        agent_phrase = value.get_links("agent")[0]
        tokens = get_all_tokens(agent_phrase)
        sorted_tokens = sorted(tokens.items(), key=lambda x: x[0])
        text = ""

        for token in sorted_tokens:
            if token[1].form in ('が', 'は') or token[1].pos == '名詞接尾辞':
                continue
            text += token[1].form

        return Assign(ID(text), exp)

    def function(self, value):
        func_name = ''
        if value.main_token.form == '表示':
            func_name = 'print'
            phrase = value.get_links('object')[0]
            tokens = get_all_tokens(phrase)
            sorted_tokens = sorted(tokens.items(), key=lambda x: x[0])
            result_tokens = []

            for token in sorted_tokens:
                if 'を' == token[1].form:
                    continue
                result_tokens.append(token[1])

            exp = self.exp(result_tokens)

            return Function(func_name, exp)

    def list(self, value):
        pass

    def stmt(self, value):
        # 代入文
        if value.main_token.pos == '動詞語幹':
            if value.main_token.form == '持':
                return self.assign(value)
        if value.main_token.pos == '名詞':
            if value.main_token.form == '表示':
                return self.function(value)

    def parse(self):
        results = []
        for l in self.lexed:
            results.append(self.stmt(l))

