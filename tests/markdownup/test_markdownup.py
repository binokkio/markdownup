from pathlib import Path

from markdownup.markdownup import MarkdownUp


def test_get():

    content_root = Path(__file__) / '..' / '..' / '..' / 'test_resources' / 'markdown_repository_root'
    content_root = content_root.resolve()

    markdownup = MarkdownUp({
        'content': {
            'root': str(content_root)
        }
    })

    response = markdownup.get('index.md')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == '<h1>Hello, World!</h1>'


def test_prevent_access_outside_root():

    content_root = Path(__file__) / '..' / 'test_resources' / 'markdown_repository_root'
    content_root = content_root.resolve()

    markdownup = MarkdownUp({
        'content': {
            'root': str(content_root)
        }
    })

    response = markdownup.get('../index.md')

    assert response.status == '400 Bad Request'
    assert next(response.body, None) is None
