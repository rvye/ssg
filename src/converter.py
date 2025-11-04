from enum import Enum
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re

def text_node_to_html_node(text_node: TextNode) -> HTMLNode:
    match text_node.text_type:
        case TextType.PLAIN:
            return LeafNode('span', text_node.text)
        case TextType.BOLD:
            return LeafNode('b', text_node.text)
        case TextType.ITALIC:
            return LeafNode('i', text_node.text)
        case TextType.CODE:
            return LeafNode('code', text_node.text)
        case TextType.LINK:
            return LeafNode('a', text_node.text, props={"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode('img', "", props={"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception(f'unknown text node type: {text_node.text_type}')

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    result_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.PLAIN:
            result_nodes.append(old_node)
        else:
            ls = old_node.text.split(delimiter, maxsplit=2)
            if len(ls) == 1:
                result_nodes.append(old_node)
            elif len(ls) == 3:
                head, s, tail = ls
                parts = [
                    TextNode(head, TextType.PLAIN),
                    TextNode(s, text_type),
                    TextNode(tail, TextType.PLAIN),
                ]
                result_nodes.extend(parts)
            else:
                raise Exception('invalid Markdown syntax')

    return result_nodes

def extract_markdown_images(text: str):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    maches = re.findall(pattern, text)
    return maches


def extract_markdown_links(text: str):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    maches = re.findall(pattern, text)
    return maches

def split_nodes_image(old_nodes: list[TextNode]):
    result_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.PLAIN:
            result_nodes.append(old_node)
            continue

        images = extract_markdown_images(old_node.text)
        if len(images) == 0:
            result_nodes.append(old_node)
        else:
            rest_text = old_node.text
            for image in images:
                alt, url = image
                head, rest_text = rest_text.split(f'![{alt}]({url})', maxsplit=1)

                if head != '':
                    result_nodes.append(TextNode(head, TextType.PLAIN))
                result_nodes.append(TextNode(alt, TextType.IMAGE, url))

            if rest_text != '':
                result_nodes.append(TextNode(rest_text, TextType.PLAIN))

    return result_nodes


def split_nodes_link(old_nodes: list[TextNode]):
    result_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.PLAIN:
            result_nodes.append(old_node)
            continue

        links = extract_markdown_links(old_node.text)
        if len(links) == 0:
            result_nodes.append(old_node)
        else:
            rest_text = old_node.text
            for link in links:
                alt, url = link
                head, rest_text = rest_text.split(f'[{alt}]({url})', maxsplit=1)

                if head != '':
                    result_nodes.append(TextNode(head, TextType.PLAIN))
                result_nodes.append(TextNode(alt, TextType.LINK, url))

            if rest_text != '':
                result_nodes.append(TextNode(rest_text, TextType.PLAIN))

    return result_nodes

def text_to_textnodes(text: str) -> list[TextNode]:
    node = TextNode(text, TextType.PLAIN)
    nodes = [node]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '_', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE)
    return nodes

# BLOCKS

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = markdown.split('\n\n')
    blocks = map(lambda b: b.strip(), blocks)
    blocks = filter(lambda b: b != '', blocks)
    return list(blocks)

def block_to_block_type(block: str) -> BlockType:
    if re.match(r'^#{1,6} ', block):
        return BlockType.HEADING

    if block.startswith('```') and block.endswith('```'):
        return BlockType.CODE

    if all(line.startswith('>') for line in block.split('\n')):
        return BlockType.QUOTE

    if all(line.startswith('* ') or line.startswith('- ') for line in block.split('\n')):
        return BlockType.UNORDERED_LIST

    if all(re.match(r'^\d+\. ', line) for line in block.split('\n')):
        i = 1
        for line in block.split('\n'):
            if not line.startswith(f'{i}. '):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def block_to_children(block: str) -> list[HTMLNode]:
    nodes = []
    text = block.replace('\n', ' ')
    text_to_textnodes(text)
    textnodes = text_to_textnodes(text)
    htmlnodes = list(map(text_node_to_html_node, textnodes))
    nodes.extend(htmlnodes)
    return nodes

def markdown_to_html_node(markdown: str) -> HTMLNode:
    blocks = markdown_to_blocks(markdown)

    nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.PARAGRAPH:
                children = block_to_children(block)
                node = ParentNode('p', children)
                nodes.append(node)
            case BlockType.HEADING:
                leading, body = block.split(' ', maxsplit=1)
                lvl = len(leading)
                children = block_to_children(body)
                node = ParentNode(f'h{lvl}', children)
                nodes.append(node)
            case BlockType.CODE:
                body = block.strip('```')
                node = ParentNode('pre', [
                    LeafNode('code', body)
                ])
                nodes.append(node)
            case BlockType.QUOTE:
                body = '\n'.join(line.lstrip('> ') for line in block.split('\n'))
                children = block_to_children(body)
                node = ParentNode('blockquote', children)
                nodes.append(node)
            case BlockType.UNORDERED_LIST:
                lines = block.split('\n')
                children = []
                for line in lines:
                    line_content = line[2:]
                    textnodes = text_to_textnodes(line_content)
                    htmlnodes = list(map(text_node_to_html_node, textnodes))
                    li = ParentNode('li', htmlnodes)
                    children.append(li)
                node = ParentNode('ul', children)
                nodes.append(node)
            case BlockType.ORDERED_LIST:
                lines = block.split('\n')
                children = []
                for line in lines:
                    line_content = line.split('. ', 1)[1]
                    textnodes = text_to_textnodes(line_content)
                    htmlnodes = list(map(text_node_to_html_node, textnodes))
                    li = ParentNode('li', htmlnodes)
                    children.append(li)
                node = ParentNode('ol', children)
                nodes.append(node)

    root = ParentNode('div', nodes)
    return root

def extract_title(markdown: str) -> str:
    headers = re.findall(r'^# (.*)', markdown)
    if len(headers) == 0:
        raise Exception('no # header')

    return headers[0].strip()