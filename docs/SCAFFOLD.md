# Scaffold

Create new projects from deterministic, simple templates.

Python package template:
- python -m ai.cli.fresh scaffold new MyLib ./out --template python-package

Renders:
- Folders and files support {{package}} and {{project}} placeholders
- src/{{package}}/__init__.py becomes src/mylib/__init__.py

Safety:
- Refuses to overwrite non-empty destinations unless --force is passed
- Optionally initialize git with --init-git

