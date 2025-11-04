class HTMLNode():
    def __init__(self, tag: str = None, value: str = None, children = None, props: dict[str, str] = None):
        self.tag: str = tag
        self.value: str = value
        self.children: list[HTMLNode] = children
        self.props: dict[str, str] = props

    def __repr__(self):
        html = self.to_html()
        return html

    def to_html(self) -> str:
        props = '' if self.props is None else f' {self.props_to_html()}'
        content = self.value if self.children is None else f'{self.children!r}'
        return f'<{self.tag}{props}>{content}</{self.tag}'

    def props_to_html(self):
        if self.props is None:
            return ''

        pairs = []
        for key, value in self.props.items():
            pairs.append(f'{key}="{value}"')
        return " ".join(pairs)

class LeafNode(HTMLNode):
    def __init__(self, tag: str, value: str, props: dict = None):
        super().__init__(tag, value, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError('leaf node must have a value')
        if self.tag is None:
            return f'{self.value}' 

        props_html = ''
        if self.props is not None:
            props_html = ' ' + self.props_to_html()

        return f'<{self.tag}{props_html}>{self.value}</{self.tag}>'

class ParentNode(HTMLNode):
    def __init__(self, tag: str, children: list[HTMLNode], props: dict = None):
        super().__init__(tag, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("parent node must have a tag")
        if self.children is None:
            raise ValueError("parent node must have children")

        children_html = ''
        for child in self.children:
            children_html += child.to_html()

        props_html = ''
        if self.props is not None:
            props_html = ' ' + self.props_to_html()

        return f'<{self.tag}{props_html}>{children_html}</{self.tag}>'

        