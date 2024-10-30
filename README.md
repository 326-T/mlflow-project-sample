# MLflow project sample

MLflowのプロジェクトのサンプル.

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

- `MLproject`: MLflowプロジェクトの設定ファイル
- `main.py`: プロジェクトのエントリポイント
- `Dockerfile`: プロジェクトのDockerfile
- `.kube/job_template.yaml`: Kubernetesジョブのテンプレート
- `.kube/kubernetes_config.yaml`: デプロイ対象のクラスタに関する設定ファイル

## プロジェクトの実行
### ローカルでの実行
```bash
$ MLFLOW_TRACKING_URI=http://localhost:5001 mlflow run . --experiment-name wine_quality -P alpha=0.5 --build-image
```

### Kubernetesでの実行
namespaceを作成する.
```bash
$ kubectl create ns mlflow
```

kubernetesクラスタ内にMLflow Tracking Serverをデプロイする.<br/>
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
| KUBE_MLFLOW_TRACKING_URI | mlflow project インスタンスからアクセスできるMLflowサーバのURL |
| MLFLOW_TRACKING_URI | mlflowクライアントからアクセスできるMLflowサーバのURL |
