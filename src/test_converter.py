import unittest

from textnode import TextNode, TextType
from htmlnode import LeafNode, ParentNode
from converter import (
    text_node_to_html_node, 
    split_nodes_delimiter, 
    extract_markdown_images, 
    extract_markdown_links, 
    split_nodes_image, 
    split_nodes_link, 
    text_to_textnodes, 
    markdown_to_blocks,
    block_to_block_type,
    markdown_to_html_node,
    extract_title,
    BlockType
)


class TestConverter(unittest.TestCase):
    def test_plain_text_node(self):
        text_node = TextNode("This is a plain text", TextType.PLAIN)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "span")
        self.assertEqual(html_node.value, "This is a plain text")

    def test_bold_text_node(self):
        text_node = TextNode("This is bold text", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold text")

    def test_italic_text_node(self):
        text_node = TextNode("This is italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is italic text")

    def test_code_text_node(self):
        text_node = TextNode("This is code", TextType.CODE)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is code")

    def test_link_text_node(self):
        text_node = TextNode("Google", TextType.LINK, "https://www.google.com")
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props, {"href": "https://www.google.com"})

    def test_image_text_node(self):
        text_node = TextNode("My image", TextType.IMAGE, "/path/to/image.jpg")
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.props, {"src": "/path/to/image.jpg", "alt": "My image"})

    def test_unknown_text_node_type(self):
        text_node = TextNode("Unknown", "unknown_type")
        with self.assertRaises(Exception) as cm:
            text_node_to_html_node(text_node)
        self.assertIn("unknown text node type", str(cm.exception))

    def test_split_nodes_delimiter(self):
        node = TextNode("This is text with a `code` word", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.PLAIN),
                TextNode("code", TextType.CODE),
                TextNode(" word", TextType.PLAIN),
            ],
        )

    def test_split_nodes_delimiter_bold(self):
        node = TextNode("This is text with **bold** word", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
                TextNode(" word", TextType.PLAIN),
            ],
        )

    def test_split_nodes_delimiter_invalid_markdown(self):
        node = TextNode("This is text with `code word", TextType.PLAIN)
        with self.assertRaises(Exception) as cm:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("invalid Markdown syntax", str(cm.exception))

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("This is text without a delimiter", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [node])

    def test_split_nodes_delimiter_non_plain_node(self):
        node1 = TextNode("This is plain text", TextType.PLAIN)
        node2 = TextNode("This is bold text", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        self.assertEqual(new_nodes, [node1, node2])

    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://example.com/image.png) and another ![alt text](https://example.com/another.jpg)"
        self.assertEqual(extract_markdown_images(text), [("image", "https://example.com/image.png"), ("alt text", "https://example.com/another.jpg")])

    def test_extract_markdown_images_no_images(self):
        text = "This is text with no images."
        self.assertEqual(extract_markdown_images(text), [])

    def test_extract_markdown_links(self):
        text = "This is text with a [link](https://example.com) and another [link two](https://example.com/two)"
        self.assertEqual(extract_markdown_links(text), [("link", "https://example.com"), ("link two", "https://example.com/two")])

    def test_extract_markdown_links_no_links(self):
        text = "This is text with no links."
        self.assertEqual(extract_markdown_links(text), [])

    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with an ![image](https://example.com/image.png) and another ![alt text](https://example.com/another.jpg)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://example.com/image.png"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode("alt text", TextType.IMAGE, "https://example.com/another.jpg"),
            ],
        )

    def test_split_nodes_image_single_image(self):
        node = TextNode("![image](https://example.com/image.png)", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertEqual(
            new_nodes,
            [TextNode("image", TextType.IMAGE, "https://example.com/image.png")],
        )

    def test_split_nodes_image_with_trailing_text(self):
        node = TextNode("this is text ![image](http://example.com/image.png) for you", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("this is text ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "http://example.com/image.png"),
                TextNode(" for you", TextType.PLAIN),
            ],
        )

    def test_split_nodes_link(self):
        node = TextNode(
            "This is text with a [link](https://example.com) and another [link two](https://example.com/two)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode("link two", TextType.LINK, "https://example.com/two"),
            ],
        )

    def test_split_nodes_link_single_link(self):
        node = TextNode("[link](https://example.com)", TextType.PLAIN)
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [TextNode("link", TextType.LINK, "https://example.com")],
        )

    def test_split_nodes_link_with_trailing_text(self):
        node = TextNode("this is text [link](http://example.com) for you", TextType.PLAIN)
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("this is text ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "http://example.com"),
                TextNode(" for you", TextType.PLAIN),
            ],
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![image](https://example.com/image.png) and a [link](https://example.com)"
        nodes = text_to_textnodes(text)
        self.assertEqual(
            nodes,
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.PLAIN),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://example.com/image.png"),
                TextNode(" and a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text."
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes, [TextNode("This is just plain text.", TextType.PLAIN)])

    def test_text_to_textnodes_empty_string(self):
        text = ""
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes, [TextNode("", TextType.PLAIN)])


    # BLOCKS TEST
    def test_markdown_to_blocks(self):
        markdown = """
# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item
        """

        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
            """* This is the first list item in a list block\n* This is a list item\n* This is another list item""",
        ])

    def test_markdown_to_blocks_multiple_paragraphs(self):
        markdown = """
This is the first paragraph.

This is the second paragraph. It has some **bold** text.

And this is the third paragraph.
        """
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [
            "This is the first paragraph.",
            "This is the second paragraph. It has some **bold** text.",
            "And this is the third paragraph.",
        ])

    def test_markdown_to_blocks_mixed_content(self):
        markdown = """
# Heading 1

This is a paragraph.

```
Code block
```

> This is a quote.

- List item 1
- List item 2
        """
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [
            "# Heading 1",
            "This is a paragraph.",
            "```\nCode block\n```",
            "> This is a quote.",
            """- List item 1\n- List item 2""",
        ])

    def test_markdown_to_blocks_leading_trailing_newlines_spaces(self):
        markdown = """

        # Heading with spaces

    This is a paragraph with leading spaces.


        """
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [
            "# Heading with spaces",
            "This is a paragraph with leading spaces.",
        ])

    def test_markdown_to_blocks_empty_string(self):
        markdown = ""
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_only_newlines(self):
        markdown = """


        """
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [])

    # BLOCK_TO_BLOCK_TYPE
    def test_block_to_block_type_heading(self):
        block = "# Heading 1"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_code(self):
        block = "```\nCode block\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_quote(self):
        block = "> This is a quote."
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_unordered_list(self):
        block = "- List item 1\n- List item 2"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ordered_list(self):
        block = "1. List item 1\n2. List item 2"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_paragraph(self):
        block = "This is a paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_invalid_heading(self):
        block = "####### Invalid Heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_invalid_quote(self):
        block = "> This is a quote.\nThis is not a quote."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_invalid_unordered_list(self):
        block = "- List item 1\nThis is not a list item."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_invalid_ordered_list(self):
        block = "1. List item 1\n3. List item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_markdown_to_html_node_paragraph(self):
        markdown = "This is a simple paragraph."
        node = markdown_to_html_node(markdown)
        expected = ParentNode(
            "div",
            [
                ParentNode(
                    "p",
                    [
                        LeafNode("span", "This is a simple paragraph.")
                    ],
                )
            ],
        )
        self.assertEqual(node.to_html(), expected.to_html())

    def test_markdown_to_html_node_heading(self):
        markdown = "## This is a heading"
        node = markdown_to_html_node(markdown)
        expected = ParentNode(
            "div",
            [
                ParentNode(
                    "h2",
                    [LeafNode("span", "This is a heading")],
                )
            ],
        )
        self.assertEqual(node.to_html(), expected.to_html())

    def test_markdown_to_html_node_code(self):
        markdown = """```code block```"""
        node = markdown_to_html_node(markdown)
        expected = ParentNode(
            "div",
            [ParentNode("pre", [LeafNode("code", "code block")])],
        )
        self.assertEqual(node.to_html(), expected.to_html())

    def test_markdown_to_html_node_quote(self):
        markdown = "> quote line 1\n> quote line 2"
        node = markdown_to_html_node(markdown)
        expected = ParentNode(
            "div",
            [
                ParentNode(
                    "blockquote",
                    [
                        LeafNode("span", "quote line 1 quote line 2")
                    ],
                )
            ],
        )
        self.assertEqual(node.to_html(), expected.to_html())
    
    def test_markdown_to_html_node_unordered_list(self):
        markdown = "* item 1\n* item 2"
        node = markdown_to_html_node(markdown)
        expected = ParentNode(
            "div",
            [
                ParentNode(
                    "ul",
                    [
                        ParentNode("li", [LeafNode("span", "item 1")]),
                        ParentNode("li", [LeafNode("span", "item 2")]),
                    ],
                )
            ],
        )
        self.assertEqual(node.to_html(), expected.to_html())

    def test_markdown_to_html_node_ordered_list(self):
        markdown = "1. item 1\n2. item 2"
        node = markdown_to_html_node(markdown)
        expected = ParentNode(
            "div",
            [
                ParentNode(
                    "ol",
                    [
                        ParentNode("li", [LeafNode("span", "item 1")]),
                        ParentNode("li", [LeafNode("span", "item 2")]),
                    ],
                )
            ],
        )
        self.assertEqual(node.to_html(), expected.to_html())

    def test_markdown_to_html_node_mixed(self):
        markdown = '''
# Welcome

This is a paragraph with **bold** and _italic_ text.

- list item 1
- list item 2

Check this out:

1. One
2. Two
'''
        node = markdown_to_html_node(markdown)
        expected = ParentNode("div", [
            ParentNode("h1", [LeafNode("span", "Welcome")]),
            ParentNode("p", [
                LeafNode("span", "This is a paragraph with "),
                LeafNode("b", "bold"),
                LeafNode("span", " and "),
                LeafNode("i", "italic"),
                LeafNode("span", " text."),
            ]),
            ParentNode("ul", [
                ParentNode("li", [LeafNode("span", "list item 1")]),
                ParentNode("li", [LeafNode("span", "list item 2")]),
            ]),
            ParentNode("p", [LeafNode("span", "Check this out:")]),
            ParentNode("ol", [
                ParentNode("li", [LeafNode("span", "One")]),
                ParentNode("li", [LeafNode("span", "Two")]),
            ]),
        ])
        
        self.assertEqual(node.to_html(), expected.to_html())

    def test_extract_title(self):
        markdown = "# This is a title"
        title = extract_title(markdown)
        self.assertEqual(title, "This is a title")

        markdown = "# This is a title with spaces   "
        title = extract_title(markdown)
        self.assertEqual(title, "This is a title with spaces")

        markdown_no_title = "This is a paragraph without a title."
        with self.assertRaises(Exception) as cm:
            extract_title(markdown_no_title)
        self.assertEqual("no # header", str(cm.exception))

        markdown_not_h1 = "## This is not a title"
        with self.assertRaises(Exception) as cm:
            extract_title(markdown_not_h1)
        self.assertEqual("no # header", str(cm.exception))

        markdown_with_content_before = "This is a paragraph.\n# This is a title"
        with self.assertRaises(Exception) as cm:
            extract_title(markdown_with_content_before)
        self.assertEqual("no # header", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
