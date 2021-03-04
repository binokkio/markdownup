# MarkdownUp

MarkdownUp is a Markdown server that turns a set of Markdown documents into a website.
The main features are:

- per directory group and/or role based authorization
- integration with external authentication solutions through Keycloak
- display of versioning information from Git
- interactive tree view of the served directories and Markdown files
- basic search functionality
- themeable with [Mustache templates](https://mustache.github.io/)
- support for [Markdown extensions](https://python-markdown.github.io/extensions/)


## Installation

`pip install markdownup`


## Usage

`python -m markdownup path/to/markdown/root`

Or

`python -m markdownup --start-config config.yml`

After which the config.yml can be edited to suit your needs, and the MarkdownUp server launched with:

`python -m markdownup config.yml`


## Configuration

The configuration file created by the --start-config flag contains the default settings.
The configuration of features that are not configured by default is described here.


### Access control

MarkdownUp will look for a file with the name as configured at `access.filename` in each content directory.
This file should contain the roles and groups with access to the parent directory of the access file.
The structure of this file is simply 1 role or group per line.
MarkdownUp will respond with a 404 Not Found for files which the authenticated user does not have access to.
The 404 is given instead of a 401/403 to prevent exposing that content exists for the given URL.

Authentication is not configured by default meaning that any directory with a non-empty access file will be inaccessible.
The following sections describe different authentication configurations. 


#### Authentication with HTTP basic auth

The `access` YAML structure can be extended as follows to get started with HTTP basic auth.

```
access:
  filename: .upaccess
  auth:
    type: basic-auth
    realm: actual-realm-name
    users:
      actual-user-name:
        password: plain-text-password
        roles:
        - actual-role-1
        - actual-role-2
```


#### Authentication with Keycloak

The `access` YAML structure can be extended as follows to get started with Keycloak auth.

```
access:
  filename: .upaccess
  auth:
    type: keycloak
    auth_url: 
    redirect_url: 
    realm: 
    client_id: 
    display_name: preferred_username
    roles:
    - realm_access.roles
    cookie:
      path: /
      max_age: 2592000
```

|Configuration key         |Description                                                                                       |
|--------------------------|--------------------------------------------------------------------------------------------------|
|access.filename           |Name of file containing the groups and roles with access to the files parent directory            |
|access.auth.type          |Type of auth provider, currently only "keycloak" is a valid option                                |
|access.auth.auth_url      |The root URL of the Keycloak instance to use                                                      |
|access.auth.redirect_url  |The root URL of the MarkdownUp instance to redirect back to from Keycloak                         |
|access.auth.realm         |The Keycloak realm to use                                                                         |
|access.auth.client_id     |The Keycloak client id to use                                                                     |
|access.auth.display_name  |The key in the Keycloak access token from which to take the display name of the authenticated user|
|access.auth.roles         |List of keys in the Keycloak access token from which to take the roles of the authenticated user  |
|access.auth.cookie.path   |Value for the cookie Path attribute, defaults to '/'                                              |
|access.auth.cookie.max_age|Value for the cookie Max-Age attribute, defaults to 2592000                                       |


### Redis cache

MarkdownUp can use Redis for caching and storing auth sessions, configuration is as follows:

```
cache:
  type: redis
  host: 127.0.0.1
  port: 6379
  db: 0
```


### Asset ETag

MarkdownUp considers all non-Markdown files to be assets.
Add `etag_assets: true` in the `content` configuration section to enable asset etagging.
Asset files inside Git repositories will be tagged with the commit hash in which they were last modified.
Asset files outside of Git repositories will be tagged with a sha1 hash of their file last modified timestamp.
The etags are created during MarkdownUp start-up and file modifications are not monitored.
See the [MDN ETag documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag) for more information on ETags.


### Render config

Extra data can be made available to the HTML templates by adding a `render` section in the config YAML. E.g.:

```
render:
  example: value
  css:
  - /extra.css
```

The default theme will include css files configured this way.


## Custom themes

Run `python -m markdownup --start-theme theme-name` to get started with a new theme.
Add the path to the new theme in the config YAML at `theme`.
Modify the files in the theme directory to get the desired result.
