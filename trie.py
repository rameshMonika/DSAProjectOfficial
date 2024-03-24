# trie.py
class TrieNode:
    def __init__(self):
        self.children = {}
        self.finishedEntry = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.finishedEntry = True

    def get_suggestions(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self.wordsuggestions(node, "", prefix)

    def wordsuggestions(self, node, word, prefix):
        suggestions = []
        if node.finishedEntry:
            suggestions.append(prefix + word)
        for a, n in node.children.items():
            suggestions.extend(self.wordsuggestions(n, word + a, prefix))
        return suggestions