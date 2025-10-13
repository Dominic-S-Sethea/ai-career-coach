data:
    python src/data/make_dataset.py

features:
    python src/features/build_features.py

train:
    python src/models/train_model.py

docker:
    docker build -t career-coach .