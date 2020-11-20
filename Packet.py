import sys

class Packet() :
    def __init__(self, no, content):
        self.no = no
        self.content = content
        self.tag = 0

    def get_size(self):
        return sys.getsizeof(self.content)

    def get_no(self):
        return self.no

    def add_tag(self, _tag):
        self.tag = _tag

    def get_tag(self):
        return self.tag.get_createTime()

