from pathlib import Path

from markdownup.config import Config
from markdownup.markdownup import MarkdownUp
from markdownup.search.search_provider import search


def test_get():

    markdownup = MarkdownUp(Config.from_dict({
        'theme': 'bare',
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs'),
            'indices': []
        }
    }))

    response = markdownup.get('/index.md')

    assert response.status == '200 OK'
    assert response.body[0] == b'<h1>Hello, World!</h1>\n<p>This is a markdown file.</p>'


def test_prevent_access_outside_root():

    markdownup = MarkdownUp(Config.from_dict({
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs' / 'subdir')}
    }))

    response = markdownup.get('../index.md')

    assert response.status == '400 Bad Request'
    assert response.body[0] == b'400 Bad Request'


def test_with_fs_theme():

    markdownup = MarkdownUp(Config.from_dict({
        'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme'),
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs'),
            'indices': []
        }
    }))

    response = markdownup.get('/index.md')

    assert response.status == '200 OK'
    assert response.body[0] == b'Title goes here: Hello, World!\n\nContent goes here:\n\n<h1>Hello, World!</h1>\n<p>This is a markdown file.</p>'


def test_serve_non_markdown_file():

    markdownup = MarkdownUp(Config.from_dict({
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs')}
    }))

    response = markdownup.get('/dummy-asset.txt')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == 'Dummy asset content.'


def test_title_not_on_first_line():

    markdownup = MarkdownUp(Config.from_dict({
        'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme'),
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs')}
    }))

    response = markdownup.get('/title_not_on_first_line.md')

    assert response.status == '200 OK'
    assert response.body[0] == b'Title goes here: Title\n\nContent goes here:\n\n<p>Some text first.</p>\n<h1>Title</h1>'


def test_hidden_directory_request_yields_404():

    # 404 because we don't want to expose the fact it exists

    markdownup = MarkdownUp(Config.from_dict({
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs')}
    }))

    response = markdownup.get('/.hidden/hidden.md')

    assert response.status == '404 Not Found'
    # TODO check response body, ensure there is no content


def test_hidden_file_request_yields_404():

    # 404 because we don't want to expose the fact it exists

    markdownup = MarkdownUp(Config.from_dict({
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs')}
    }))

    response = markdownup.get('/.hidden.md')

    assert response.status == '404 Not Found'
    # TODO check response body, ensure there is no content


def test_get_theme_asset():

    markdownup = MarkdownUp(Config.from_dict({
        'theme': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'test_theme'),
        'content': {'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs')}
    }))

    response = markdownup.get('/frame.css')

    assert response.status == '200 OK'
    assert next(response.body).decode('UTF-8') == 'p { color: #111; }'


def test_get_hidden_file_with_proper_config():

    markdownup = MarkdownUp(Config.from_dict({
        'theme': 'bare',
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs'),
            'exclusions': []
        }
    }))

    response = markdownup.get('/.hidden.md')

    assert response.status == '200 OK'
    assert response.body[0] == b'<p>This file must not be served with the default configuration.</p>'


def test_search():

    markdownup = MarkdownUp(Config.from_dict({
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs')
        }
    }))

    results = search(markdownup, {'auth': {}}, ["THIS"])

    assert len(results) == 2
    assert results[0].name == 'Hello, World!'
    assert results[1].name == 'Hello, nested World!'


def test_search_with_auth():

    markdownup = MarkdownUp(Config.from_dict({
        'content': {
            'root': str(Path(__file__).parent / '..' / '..' / 'test_resources' / 'dummy_docs'),
        }
    }))

    results = search(markdownup, {
        'auth': {
            'authenticated': {
                'roles': {
                    'keepers'
                }
            }
        }
    }, ["THIS"])

    assert len(results) == 3
    assert results[0].name == 'Hello, World!'
    assert results[1].name == 'Hello, nested World!'
    assert results[2].name == 'Hello, secret nested World!'
