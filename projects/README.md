# MLflow project sample

MLflow のプロジェクトのサンプル.

## プロジェクトの構成

```
../
├── .github
│   └── workflows
│       └── projects
│           ├── wine-quality.yml
│           └── another_project.yml
└── projects
    ├── wine-quality
    |   ├── .venv
    |   ├── Dockerfile
    |   ├── main.py
    |   └── requirements.txt
    └── another_project
        ├── .venv
        ├── Dockerfile
        ├── main.py
        └── requirements.txt
```

- `main.py`: プロジェクトのエントリポイント
- `Dockerfile`: プロジェクトの Dockerfile
- `.kube/job_template.yaml`: Kubernetes ジョブのテンプレート
- `.kube/kubernetes_config.yaml`: デプロイ対象のクラスタに関する設定ファイル

## project の作成

```bash
$ mkdir -p projects/wine-quality
$ cd projects/wine-quality
$ python3.10 -m venv .venv
$ source .venv/bin/activate
$ pip install --upgrade pip
$ pip install mlflow ...and so on
$ pip freeze > requirements.txt
```

## プロジェクトの実行

### プロジェクトのビルド

```bash
$ cd projects/wine-quality
$ docker build -t wine-quality:latest .
```

### ローカルでの実行

MLflow Tracking Server を起動する.

```bash
$ mlflow server --host localhost --port 8080
```

GUI で[MLflow Tracking](http://localhost:8080)にアクセスし、`wine-quality`の`Experiment`を作成する.

```bash
$ docker run \
  -e MLFLOW_TRACKING_URI=http://localhost:8080 \
  -e MLFLOW_EXPERIMENT_ID=430758536676277373 \
  --add-host="localhost:host-gateway" \
  wine-quality:latest
```
