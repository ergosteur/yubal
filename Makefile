.PHONY: dev css watch

dev: css
	uv run python run.py

css:
	./tailwindcss -i styles.css -o ./app/static/css/output.css --minify

watch:
	./tailwindcss -i styles.css -o ./app/static/css/output.css --watch
