from copy import deepcopy

default_config = {
    'wsgi': {
        'bind': '127.0.0.1:8080',
        'workers': 1
    },
    'content': {
        'theme': 'default',
        'indices': [
            'README.md',
            'index.md'
        ]
    }
}


def extend_default_config(extension):
    config = deepcopy(default_config)
    for group, values in extension.items():
        for key, value in values.items():
            config[group][key] = value
    return config
