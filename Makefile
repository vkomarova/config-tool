PYTHON = python3

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

example:
	$(PYTHON) -m src.main -o web_server.yaml < examples/web_server.txt
	$(PYTHON) -m src.main -o game.yaml < examples/game.txt
