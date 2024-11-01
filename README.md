# MLflow project sample

MLflow のプロジェクトのサンプル.

## プロジェクトの構成

```
.
├── .github
│   └── workflows
│       └── wine-quality.yml
└── projects
    ├── wine-quality
    |   ├── .venv
    |   ├── Dockerfile
    |   ├── MLproject
    |   ├── main.py
    |   └── requirements.txt
    └── another_project
        ├── .venv
        ├── Dockerfile
        ├── MLproject
        ├── main.py
        └── requirements.txt
```

- `MLproject`: MLflow プロジェクトの設定ファイル
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
$ pip install ...
$ pip freeze > requirements.txt
```

KServe:v0.1.4 では以下のライブラリ依存が存在する
| ライブラリ | バージョン |
| --- | --- |
| mlflow | 2.10.2 |
| cloudpickle | 3.0.0 |
| tensorflow | 2.14.1 |

## プロジェクトの実行

### プロジェクトのビルド

```bash
$ cd projects/wine-quality
$ docker build -t 326takeda/mlflow-project_wine-quality:latest .
$ docker push 326takeda/mlflow-project_wine-quality:latest
```

### ローカルでの実行

MLflow Tracking Server を起動する.

```bash
$ mlflow server --host localhost --port 8080
```

```bash
$ cd projects/wine-quality
$ MLFLOW_TRACKING_URI=http://localhost:8080 \
  mlflow run . \
  --docker-args add-host="localhost:host-gateway" \
  --experiment-name wine-quality \
  -P alpha=0.5
```

### Kubernetes での実行

namespace を作成する.

```bash
$ kubectl create ns mlflow
```

kubernetes クラスタ内に MLflow Tracking Server をデプロイする.<br/>

```bash
$ helm install mlflow oci://registry-1.docker.io/bitnamicharts/mlflow --version 2.0.2 -n mlflow \
--set minio.enabled=false \
--set postgresql.enabled=false \
--set tracking.auth.enabled=false \
--set tracking.persistence.enabled=false \
--set tracking.service.type=ClusterIP
```

```bash
$ kubectl port-forward -n mlflow svc/mlflow-tracking 8081:80
```

プロジェクトを実行する.

```bash
$ KUBE_MLFLOW_TRACKING_URI=http://mlflow-tracking \
  MLFLOW_TRACKING_URI=http://localhost:8081 \
  mlflow run . \
  --experiment-name wine-quality \
  --backend kubernetes \
  --backend-config .kube/kubernetes_config.json \
  -P alpha=0.5
```

環境変数
| 環境変数 | 説明 |
| --- | --- |
| KUBE_MLFLOW_TRACKING_URI | mlflow project インスタンスからアクセスできる MLflow サーバの URL |
| MLFLOW_TRACKING_URI | mlflow クライアントからアクセスできる MLflow サーバの URL |
