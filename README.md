# MLflow project sample

MLflow のプロジェクトのサンプル.

## プロジェクトの構成

```
.
├── MLproject
├── main.py
├── Dockerfile
└── .kube
    ├── job_template.yaml
    └── kubernetes_config.yaml
```

- `MLproject`: MLflow プロジェクトの設定ファイル
- `main.py`: プロジェクトのエントリポイント
- `Dockerfile`: プロジェクトの Dockerfile
- `.kube/job_template.yaml`: Kubernetes ジョブのテンプレート
- `.kube/kubernetes_config.yaml`: デプロイ対象のクラスタに関する設定ファイル

## project の作成

```bash
$ python3.10 -m venv .venv
$ source .venv/bin/activate
$ pip install --upgrade pip
# KServeのInferenceServiceが対応しているのは以下
$ pip install mlflow==2.10.2
$ pip install cloudpickle==3.0.0
$ pip install tensorflow==2.14.1
$ pip install hyperopt
```

## プロジェクトの実行

### ローカルでの実行

```bash
$ MLFLOW_TRACKING_URI=http://localhost:5001 mlflow run . --experiment-name wine_quality -P alpha=0.5 --build-image
```

### Kubernetes での実行

namespace を作成する.

```bash
$ kubectl create ns mlflow
```

kubernetes クラスタ内に MLflow Tracking Server をデプロイする.<br/>

```bash
$ helm install my-mlflow oci://registry-1.docker.io/bitnamicharts/mlflow --version 2.0.2 -n mlflow
$ kubectl port-forward -n mlflow svc/my-mlflow 5001:80
```

プロジェクトを実行する.

```bash
$ docker build -t mlflow-sample-project:latest .
$ KUBE_MLFLOW_TRACKING_URI=http://my-mlflow MLFLOW_TRACKING_URI=http://localhost:5001 mlflow run . --experiment-name wine_quality --backend kubernetes --backend-config .kube/kubernetes_config.json -P alpha=0.5
```

環境変数
| 環境変数 | 説明 |
| --- | --- |
| KUBE_MLFLOW_TRACKING_URI | mlflow project インスタンスからアクセスできる MLflow サーバの URL |
| MLFLOW_TRACKING_URI | mlflow クライアントからアクセスできる MLflow サーバの URL |
