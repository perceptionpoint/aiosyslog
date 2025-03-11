package:
	python3.12 -m pip install build
	python3.12 -m build

debug:
	python3.12 -m venv venv
	venv/bin/python -m pip install -e .
	venv/bin/python -m pip install ipython
	cd venv/bin && ./ipython && cd ../../

clean:
	rm -rf dist
	rm -rf aiosyslog.egg-info
	rm -rf venv
