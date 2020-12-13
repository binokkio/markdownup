from typing import Dict, List

import chevron

from markdownup.filesystem.markdown_file import MarkdownFile
from markdownup.response import Response


def search(context, environ, search_terms):
    search_scores: Dict[MarkdownFile, float] = {}

    for markdown_file in context.root.get_markdown_files(environ):
        score = 0.0
        for term in search_terms:
            term_score = markdown_file.search_index.get(term.lower(), 0.0)
            if term_score:
                score += 1.0 / term_score
        if score:
            search_scores[markdown_file] = score

    search_results: List[MarkdownFile] = \
        [entry[0] for entry in sorted(search_scores.items(), key=lambda entry: entry[1], reverse=True)]

    return search_results


def get_search_response(context, environ, request):

    search_terms = request['terms'][0]
    search_results = search(context, environ, search_terms.split(' '))

    html = chevron.render(
        template=context.theme.html['search-results'],
        partials_dict=context.theme.html,
        data={
            'title': 'Search results',
            'root': context.root,
            'auth': environ.get('auth', None),
            'search_terms': search_terms,
            'search_results': search_results
        }
    )

    return Response(
        '200 OK',
        [('Content-Type', 'text/html')],
        (bytes(b, 'UTF-8') for b in html.splitlines(keepends=True))
    )
