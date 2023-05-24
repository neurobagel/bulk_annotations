.PHONY: openneuro openneuro-derivatives

install:
	pip install -r requirements.txt

clear:
	rm -rf inputs

openneuro:
	mkdir -p inputs
	cd inputs && datalad install ///openneuro --recursive -J 12

openneuro-derivatives:
	mkdir -p inputs
	cd inputs && datalad install ///openneuro-derivatives --recursive -J 12

outputs/openneuro.tsv:
	python list_openneuro_dependencies.py

outputs/list_participants_tsv_columns.py: outputs/openneuro.tsv
	python list_participants_tsv_columns.py

outputs/list_participants_tsv_levels.py: outputs/openneuro.tsv
	python list_participants_tsv_levels.py
