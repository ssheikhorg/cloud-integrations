install:
	python -m pip install --upgrade pip && pip install -U -r ./src/layer/requirements.txt

dev:
	python -m pip install --upgrade pip && pip install -r ./requirements-dev.txt

ias:
	pip install --upgrade pip && pip install -r ./requirements.txt

clean:
	pyclean .

type:
	mypy src/
