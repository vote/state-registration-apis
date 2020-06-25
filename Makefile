
lint:
	autoflake \
		--remove-unused-variables \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		--in-place \
		--recursive \
		ovrlib/ *.py && \
		isort --recursive ovrlib/ *.py && \
		black ovrlib/ *.py


test:
	python -m pytest .
