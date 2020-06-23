
lint:
	autoflake \
		--remove-unused-variables \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		--in-place \
		--recursive \
		ovrlib/ && \
		isort --recursive ovrlib/ && \
		black ovrlib/
