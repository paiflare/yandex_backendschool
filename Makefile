.PHONY: migrate clean

migrate:
	@alembic upgrade head

clean:
	@rm -rf .mypy_cache
	@rm -rf .eggs
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf *.egg-info
	@rm -rf .coverage
	@rm -rf .coverage.xml
	@rm -rf dist/
	@rm -rf build/
