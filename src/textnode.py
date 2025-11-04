from enum import Enum

class TextType(Enum):
    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode():
    def __init__(self, text: str, text_type: TextType, url: str=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, value):
        if  self.text == value.text \
            and self.text_type == value.text_type\
            and self.url == value.url:
            return True
        else:
            return False

    def __repr__(self):
        if self.url != None:
            return f'TextNode("{self.text}", {self.text_type.value}, <{self.url}>)'
        else:
            return f'TextNode("{self.text}", {self.text_type.value})'

    