# KServe Predictors

MLflow のプロジェクトのサンプル.

## Predictors の構成

```
../
├── .github
│   └── workflows
│       └── predictors
│           ├── sentence-transformer.yml
│           └── another-predictor.yml
└── predictors
    ├── sentence-transformer
    |   ├── Procfile
    |   ├── model.py
    |   └── requirements.txt
    └── another_predictors
        ├── Procfile
        ├── model.py
        └── requirements.txt
```

- `Procfile`: プロジェクトの Dockerfile
- `model.py`: Predictor のエントリポイント

## Predictors の作成

```bash
$ mkdir -p predictors/another-predictor
$ cd predictors/another-predictor
$ python3.10 -m venv .venv
$ source .venv/bin/activate
$ pip install --upgrade pip
$ pip install mlflow ...and so on
$ pip freeze > requirements.txt
```

## Predictors の実行

イメージビルド

```bash
$ cd predictors/another-predictor
$ docker build -t another-predictor:latest .
```

コンテナの起動

```bash
$ docker run \
  -e PORT=8080 \
  -v mlflow-models:/mnt/models \
  -p 8080:8080 \
  another-predictor:latest
```
