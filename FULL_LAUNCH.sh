export PYTHONPATH=$(pwd)

poetry run \
	python src/main.py \
	-i data/train_dataset_atom_train.zip
