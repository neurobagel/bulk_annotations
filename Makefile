.PHONY: openneuro openneuro-derivatives

clear:
	rm -rf inputs

openneuro:
	mkdir -p inputs
	cd inputs && datalad install ///openneuro --recursive -J 12

openneuro-derivatives:
	mkdir -p inputs
	cd inputs && datalad install ///openneuro-derivatives --recursive -J 12
