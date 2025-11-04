from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re

def text_node_to_html_node(text_node: TextNode) -> HTMLNode:
    match text_node.text_type:
        case TextType.PLAIN:
            return LeafNode('p', text_node.text)
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