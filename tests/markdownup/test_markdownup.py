from pathlib import Path

from markdownup.config import extend_default_config
from markdownup.markdownup import MarkdownUp


def test_get():

    markdownup = MarkdownUp(extend_default_config({
        'main': {'theme': 'bare'},
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root'),
            'indices': []
        }
    }))

    response = markdownup.get('index.md')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == '<h1>Hello, World!</h1>\n'


def test_prevent_access_outside_root():

    markdownup = MarkdownUp(extend_default_config({
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root' / 'subdir')}
    }))

    response = markdownup.get('../index.md')

    assert response.status == '400 Bad Request'
    assert next(response.body, None) is None


def test_with_fs_theme():

    markdownup = MarkdownUp(extend_default_config({
        'main': {'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme')},
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root'),
            'indices': []
        }
    }))

    response = markdownup.get('index.md')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == 'Title goes here: Hello, World!\n'


def test_serve_non_markdown_file():

    markdownup = MarkdownUp(extend_default_config({
        'main': {'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme')},
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root')}
    }))

    response = markdownup.get('/frame.css')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == 'p { color: #111; }'


def test_title_not_on_first_line():

    markdownup = MarkdownUp(extend_default_config({
        'main': {'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme')},
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'markdown_repository_root')}
    }))

    response = markdownup.get('title_not_on_first_line.md')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == 'Title goes here: Title\n'
