import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_neq(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("Hello", TextType.PLAIN)
        self.assertNotEqual(node1, node2)
    
    def test_create(self):
        node1 = TextNode("Good",  TextType.ITALIC)
        self.assertEqual(node1.text, "Good")
        self.assertEqual(node1.text_type, TextType.ITALIC)
        self.assertIsNone(node1.url)


if __name__ == "__main__":
    unittest.main()