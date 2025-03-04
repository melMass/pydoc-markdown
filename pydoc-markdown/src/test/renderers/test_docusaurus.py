import json
from pathlib import Path

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.docusaurus import DocusaurusRenderer
from ..utils import assert_text_equals

DOCUSAURUS_TESTCASES_DIR = Path(__file__).parent.parent / 'testcases' / 'renderers' / 'docusaurus'


def test_full_processing():
    docs_path = DOCUSAURUS_TESTCASES_DIR / "docs"
    config = PydocMarkdown(
        loaders=[PythonLoader(
            search_path=[str(DOCUSAURUS_TESTCASES_DIR)],
            packages=['a_test_package']
        )],
        processors=[FilterProcessor(skip_empty_modules=True), CrossrefProcessor(), SmartProcessor()],
        renderer=DocusaurusRenderer(
            docs_base_path=str(docs_path.resolve()),
            sidebar_top_level_label="Code reference",
        ),
    )

    modules = config.load_modules()
    config.process(modules)
    config.render(modules)

    sidebar = docs_path / "reference" / "sidebar.json"
    init_md = docs_path / "reference" / "a_test_package" / "module" / "__init__.md"
    wrong_module_init_md = docs_path / "reference" / "a_test_package" / "module.md"
    suff_md = docs_path / "reference" / "a_test_package" / "module" / "stuff.md"
    other_suff_md = docs_path / "reference" / "a_test_package" / "module" / "other_stuff.md"
    assert (docs_path / "reference").is_dir()
    assert sidebar.exists()
    assert suff_md.exists()
    assert init_md.exists()
    assert not wrong_module_init_md.exists()
    assert not (docs_path / "reference" / "a_test_package" / "no_docstrings.md").exists()

    with sidebar.open("r") as handle:
        sidebar = json.load(handle)

    assert sidebar == {
      "items": [
        {
          "items": [
            {
              "items": [
                "reference/a_test_package/module/__init__",
                "reference/a_test_package/module/other_stuff",
                "reference/a_test_package/module/stuff"
              ],
              "label": "a_test_package.module",
              "type": "category"
            }
          ],
          "label": "a_test_package",
          "type": "category"
        }
      ],
      "label": "Code reference",
      "type": "category"
    }

    with suff_md.open("r") as handle:
        stuff_doc = handle.read()

    assert_text_equals(stuff_doc, r"""---
sidebar_label: stuff
title: a_test_package.module.stuff
---

This is a module about stuff.

#### CONSTANT

this is a constant about stuff

#### my\_funct

```python
my_funct()
```

Do something, or nothing.

## CoolStuff Objects

```python
class CoolStuff()
```

Super cool stuff.

#### cool\_attr

This is a cool attribute.

#### run\_cool\_stuff

```python
 | run_cool_stuff()
```

Run cool stuff
""")

    with init_md.open("r") as handle:
        init_doc = handle.read()

    assert_text_equals(init_doc, r"""---
sidebar_label: module
title: a_test_package.module
---

This is module __init__.py

#### CONSTANT

This constant is rad

""")


def test_full_processing_custom_top_level_names():
    docs_path = DOCUSAURUS_TESTCASES_DIR / "a_test_package" / "docs"
    config = PydocMarkdown(
        loaders=[PythonLoader(
            search_path=[str(DOCUSAURUS_TESTCASES_DIR)],
            packages=['a_test_package']
        )],
        processors=[FilterProcessor(skip_empty_modules=True), CrossrefProcessor(), SmartProcessor()],
        renderer=DocusaurusRenderer(
        docs_base_path=str(docs_path.resolve()),
        sidebar_top_level_label=None,
        sidebar_top_level_module_label="My test package"
    ))

    modules = config.load_modules()
    config.process(modules)
    config.render(modules)

    sidebar = docs_path / "reference" / "sidebar.json"
    assert sidebar.exists()

    with sidebar.open("r") as handle:
        sidebar = json.load(handle)

    assert sidebar == {
      "items": [
        {
          "items": [
            "reference/a_test_package/module/__init__",
            "reference/a_test_package/module/other_stuff",
            "reference/a_test_package/module/stuff"
          ],
          "label": "a_test_package.module",
          "type": "category"
        }
      ],
      "label": "My test package",
      "type": "category"
    }
