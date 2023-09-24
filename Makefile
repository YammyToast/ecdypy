.PHONY: setup docs_html

setup:
	poetry config settings.virtualenvs.create true
	poetry config settings.virtualenvs.in-project true
	poetry install

docs_html:
	$(MAKE) -C docs html