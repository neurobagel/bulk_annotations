.PHONY: openneuro openneuro-derivativesv remap_openneuro

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

outputs/assessments.json:
	python src/fetch_assessments.py

outputs/assessments.tsv: outputs/assessments.json
	python src/assessments_to_tsv.py

openneuro-annotations:
	git submodule update --init --recursive

manual_files/assessments_data_dictionary.json:
	echo "You don't have the assessments data dictionary file. Please create it by following the instructions in manual_files/README.md."

outputs/vocab_map.json: openneuro-annotations outputs/assessments.tsv manual_files/assessments_data_dictionary.json
	python src/vocab_map.py

remap_openneuro: openneuro-annotations outputs/vocab_map.json
	python src/replace_in_dictionary.py

