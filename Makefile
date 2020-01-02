STATE ?=

configure:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

build:
	python render.py $(STATE)

make clean:
	rm -rf *.png
