from pathlib import Path

from markdownup.config import extend_default_config
from markdownup.markdownup import MarkdownUp


def test_get():

    markdownup = MarkdownUp(extend_default_config({
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root'),
            'theme': 'bare'
        }
    }))

    response = markdownup.get('index.md')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == '<h1>Hello, World!</h1>\n'


def test_prevent_access_outside_root():

    markdownup = MarkdownUp(extend_default_config({
        'content': {
            'root': '/tmp'
        }
    }))

    response = markdownup.get('../etc/passwd')

    assert response.status == '400 Bad Request'
    assert next(response.body, None) is None


def test_with_template():

    markdownup = MarkdownUp(extend_default_config({
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root'),
            'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme')
        }
    }))

    response = markdownup.get('index.md')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == 'Title goes here: Hello, World!\n'


def test_serve_non_markdown_file():

    markdownup = MarkdownUp(extend_default_config({
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root'),
            'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme')
        }
    }))

    response = markdownup.get('/frame.css')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == 'p { color: #111; }'
