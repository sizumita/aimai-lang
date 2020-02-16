
class Link:
    def __init__(self, info):
        self.link = info['link']
        self.label = info['label']


class Label:
    def __init__(self, label_info):
        self.label = label_info['label']
        self.token_id = label_info['token_id']


class Token:
    def __init__(self, token_info):
        self.features = token_info['features']
        self.form = token_info['form']
        self.id = token_info['id']
        self.pos = token_info['pos']
        if 'dependency_labels' in token_info.keys():
            self.dependency_labels = [Label(i) for i in token_info['dependency_labels']]

    def __str__(self):
        return self.form


class Phrase:
    def __init__(self, chunk_info):
        self.dep = chunk_info['dep']
        self.id = chunk_info['id']
        self.links = [Link(i) for i in chunk_info['links']]
        self.main_token = None
        self.sub_tokens = []
        self.child_phrases = {}

    def get_links(self, label):
        """リンク先の文節を返します"""
        results = []
        for link in self.links:
            if link.label == label:
                results.append(self.child_phrases[link.link])

        return results

    def get_link_id_list(self):
        """全てのリンク先の文節のidを返します"""
        return [i.link for i in self.links]


def lexical(data):
    phrases = {}
    mains = []
    for d in data:
        chunk_info = d['chunk_info']
        tokens = d['tokens']
        main_token = Token(tokens.pop(0))
        sub_tokens = list(map(Token, tokens))
        phrase = Phrase(chunk_info)
        phrase.main_token = main_token
        phrase.sub_tokens = {i.id: i for i in sub_tokens}

        if phrase.dep in ['O', 'P']:
            mains.append(phrase)

        phrases[phrase.id] = phrase

    for phrase in phrases.values():
        if phrase.links:
            for link in phrase.links:
                linked = phrases.get(link.link, None)
                if linked is None:
                    continue
                phrase.child_phrases[link.link] = linked

    for phrase in mains:
        if phrase.links:
            for link in phrase.links:
                linked = phrases.get(link.link, None)
                if linked is None:
                    continue
                phrase.child_phrases[link.link] = linked

    return mains

