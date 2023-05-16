.PHONY: openneuro openneuro-derivatives

clear:
	rm -rf data

openneuro:
	mkdir -p data
	cd data && datalad install ///openneuro --recursive -J 12

openneuro-derivatives:
	mkdir -p data
	cd data && datalad install ///openneuro-derivatives --recursive -J 12
