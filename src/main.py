import os
import sys
import shutil
from textnode import TextNode, TextType
from converter import extract_title,  markdown_to_html_node

def cleanup(path: str):
    print('cleanning pubic directory...')
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)


def copy_static_files(src_path: str, dst_path: str):
    if not os.path.exists(src_path):
        raise Exception("directory 'static' not exists")

    # copy
    print('starting copy files from static to public')
    for item in os.listdir(src_path):
        abs_path = os.path.join(src_path, item)
        if os.path.isfile(abs_path):
            print(f'copying {src_path}/{item} to {dst_path}/{item}')
            shutil.copy(abs_path, dst_path)
        elif os.path.isdir(abs_path):
            shutil.copytree(abs_path, os.path.join(dst_path, item))

def generate_page(base_path: str, from_path: str, template_path: str, dest_path: str):
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

    # replace url with base_path
    if base_path != '/':
        template = template.replace('href="/', f'href="{base_path}')
        template = template.replace('src="/', f'src="{base_path}')

    full_path, _ = dest_path.rsplit('/', maxsplit=1)
    os.makedirs(full_path, exist_ok=True)

    with open(dest_path, '+w') as f:
        f.write(template)

def _generate(base_path: str, src_dir: str, template_path: str, dst_dir: str):
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dst_path = os.path.join(dst_dir, item)

        if os.path.isfile(src_path) and item.endswith('.md'):
            name, _ = item.rsplit('.', maxsplit=1)
            src_path = os.path.join(src_dir, f'{name}.md')
            dst_path = os.path.join(dst_dir, f'{name}.html')
            generate_page(base_path, src_path, template_path, dst_path)
        elif os.path.isdir(src_path):
            generate_pages_recursive(base_path, src_path, template_path, dst_path)

def generate_pages_recursive(base_path: str, src_dir: str, template_path: str, dst_dir: str):
    src = os.path.abspath(src_dir)
    template = os.path.abspath(template_path)
    dst = os.path.abspath(dst_dir) 
    return _generate(base_path, src, template, dst)


def main():
    basepath = '/'
    if len(sys.argv) == 2:
        basepath = sys.argv[1]

    static_path = 'static'
    src_path = 'content'
    dst_path = 'docs'

    cleanup(dst_path)
    copy_static_files(static_path, dst_path)
    generate_pages_recursive(basepath, src_path, 'template.html', dst_path)


if __name__ == "__main__":
    main()