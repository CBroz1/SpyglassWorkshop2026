# Building Docs

## Adding new pages

`mkdocs.yml` is the site configuration file. To add a new page, edit the `nav`
section of this file. New pages should be added in the `docs/` directory.

The remainder of `mkdocs.yml` specifies the site's
[configuration](https://www.mkdocs.org/user-guide/configuration/)

## Setup

To turn on GitHub pages for your fork, you'll need to navigate to the repository
settings, and then select the 'Pages' tab on the left. From there, set pages to
be served from GitHub Actions.

## Deployment

### GitHub

From the repository, select the Actions tab, and then the 'docs' workflow on the
left. The 'Run workflow' dropdown allows you to select the branch to deploy.

## Testing

To test edits to the site, be sure docs dependencies are installed:

```console
pip install -e .[docs]
```

Then, run the build script:

```console
mkdocs build -f ./docs/mkdocs.yaml
mkdocs serve -f ./docs/mkdocs.yaml
```

This will build the site in `site/`. You can see the site by typing
`localhost:8000` into your browser.

To end the process in your console, use `ctrl+c`.

If your new submodule is causing a build error (e.g., "Could not collect ..."),
you may need to add `__init__.py` files to the submodule directories.
