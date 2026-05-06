# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Make the EduBoost app package importable by autodoc.
sys.path.insert(0, os.path.abspath("../../.."))  # repo root → app/ is importable

# -- Project information -------------------------------------------------------
project = "EduBoost SA"
copyright = "2026, EduBoost SA Team"
author = "EduBoost SA Team"
release = "2.0.0"

# -- General configuration -----------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",       # Extract docstrings automatically
    "sphinx.ext.napoleon",      # Google & NumPy style docstrings
    "sphinx.ext.viewcode",      # Link to highlighted source
    "sphinx.ext.intersphinx",   # Cross-reference Python / FastAPI docs
    "sphinx.ext.todo",          # .. todo:: directives
    "sphinx.ext.coverage",      # Coverage report for docstrings
]

# autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"

# napoleon settings (Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

# intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# todo settings
todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ---------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "titles_only": False,
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Shared assets (diagrams shared with MkDocs) — copy into _images at build time
html_extra_path = []
# The architecture SVG is symlinked/copied into _static; referenced as /_images/...
# Sphinx will pick up files placed under source/_images/


# -- Options for autodoc mock imports ------------------------------------------
# Avoid import errors for heavy dependencies not installed in the doc environment
autodoc_mock_imports = [
    "fastapi",
    "sqlalchemy",
    "asyncpg",
    "pydantic",
    "pydantic_settings",
    "jose",
    "passlib",
    "cryptography",
    "anthropic",
    "groq",
    "arq",
    "structlog",
    "stripe",
    "redis",
    "sklearn",
    "numpy",
    "scipy",
]
