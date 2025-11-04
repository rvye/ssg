import unittest

from textnode import TextNode, TextType
from htmlnode import LeafNode
from converter import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes


class TestConverter(unittest.TestCase):
    def test_plain_text_node(self):
        text_node = TextNode("This is a plain text", TextType.PLAIN)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "p")
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

if __name__ == "__main__":
    unittest.main()
