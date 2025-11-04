import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode()
        node.props = {"href": "https://www.google.com", "target": "_blank"}
        self.assertEqual(node.props_to_html(), 'href="https://www.google.com" target="_blank"')

    def test_props_to_html_single_prop(self):
        node = HTMLNode()
        node.props = {"href": "https://www.google.com"}
        self.assertEqual(node.props_to_html(), 'href="https://www.google.com"')

    def test_to_html_raises_error(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr(self):
        node = HTMLNode()
        node.tag = "p"
        node.value = "This is a paragraph."
        node.children = []
        node.props = {"class": "my-class"}
        self.assertEqual(repr(node), "<p> value:This is a paragraph. props:{'class': 'my-class'} children:[]")

    def test_leaf_node_to_html(self):
        node = LeafNode("p", "This is a paragraph.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph.</p>")

    def test_leaf_node_to_html_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_node_to_html_no_tag(self):
        node = LeafNode(None, "Just some text.")
        self.assertEqual(node.to_html(), "Just some text.")

    def test_leaf_node_to_html_no_value_raises_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_node_to_html(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_parent_node_to_html_with_props(self):
        node = ParentNode(
            "div",
            [
                LeafNode("p", "Paragraph 1"),
                LeafNode("p", "Paragraph 2"),
            ],
            {"class": "container"},
        )
        self.assertEqual(
            node.to_html(),
            '<div class="container"><p>Paragraph 1</p><p>Paragraph 2</p></div>',
        )

    def test_parent_node_to_html_nested(self):
        nested_node = ParentNode(
            "span",
            [
                LeafNode("b", "Nested bold"),
                LeafNode(None, "Nested normal"),
            ],
        )
        node = ParentNode(
            "div",
            [
                LeafNode("p", "Outer paragraph"),
                nested_node,
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div><p>Outer paragraph</p><span><b>Nested bold</b>Nested normal</span></div>",
        )

    def test_parent_node_no_tag_raises_error(self):
        node = ParentNode(None, [LeafNode("p", "text")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_node_no_children_raises_error(self):
        node = ParentNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

if __name__ == "__main__":
    unittest.main()
