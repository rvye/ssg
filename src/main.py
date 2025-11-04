import os
import shutil
from textnode import TextNode, TextType
from converter import extract_title,  markdown_to_html_node

static_dir = 'static'
public_dir = 'public'
abs_static_dir = os.path.abspath(static_dir)
abs_public_dir = os.path.abspath(public_dir)

def cleanup():
    print('cleanning pubic directory...')
    if os.path.exists(abs_public_dir):
        shutil.rmtree(abs_public_dir)
        os.mkdir(abs_public_dir)
    else:
        os.mkdir(public_dir)


def copy_static_files():
    if not os.path.exists(abs_static_dir):
        raise Exception("directory 'static' not exists")

    # copy
    print('starting copy files from static to public')
    for item in os.listdir(abs_static_dir):
        abs_path = os.path.join(abs_static_dir, item)
        if os.path.isfile(abs_path):
            print(f'copying {abs_static_dir}/{item} to {abs_public_dir}/{item}')
            shutil.copy(abs_path, abs_public_dir)
        elif os.path.isdir(abs_path):
            shutil.copytree(abs_path, os.path.join(abs_public_dir, item))

def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f'Generating page from {from_path} to {dest_path} using {template_path}')

    with open(from_path, 'r') as f:
        markdown = f.read()

    with open(template_path, 'r') as f:
        template = f.read()

    html_node = markdown_to_html_node(markdown)
    title = extract_title(markdown)
    content = html_node.to_html()

    template = template.replace('{{ Title }}', title)
    template = template.replace('{{ Content }}', content)

    full_path, _ = dest_path.rsplit('/', maxsplit=1)
    os.makedirs(full_path, exist_ok=True)

    with open(dest_path, '+w') as f:
        f.write(template)

def _generate(src_dir: str, template_path: str, dst_dir: str):
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dst_path = os.path.join(dst_dir, item)

        if os.path.isfile(src_path) and item.endswith('.md'):
            name, _ = item.rsplit('.', maxsplit=1)
            src_path = os.path.join(src_dir, f'{name}.md')
            dst_path = os.path.join(dst_dir, f'{name}.html')
            generate_page(src_path, template_path, dst_path)
        elif os.path.isdir(src_path):
            generate_pages_recursive(src_path, template_path, dst_path)

def generate_pages_recursive(src_dir: str, template_path: str, dst_dir: str):
    src = os.path.abspath(src_dir)
    template = os.path.abspath(template_path)
    dst = os.path.abspath(dst_dir) 
    return _generate(src, template, dst)


def main():
    cleanup()
    copy_static_files()
    generate_pages_recursive('content', 'template.html', 'public')


if __name__ == "__main__":
    main()