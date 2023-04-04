# cicd-e2e-lab-deploy

This repo contains the material to deploy a cicd chain on openshift.


## Deploy ArgoCD, cluster-wide subscriptions and create namespaces

```shell
oc apply -f gitops/sub.yaml
oc apply -f gitops/ns.yaml
oc apply -f gitops/ClusterRoleBinding.yaml 
```

## Configure RHACS




- Add quay authentication "registry-credentials"
- Patch build-bot
```shell
oc patch serviceaccount  \
  -p "{\"imagePullSecrets\": [{\"name\": \"registry-credentials\"}]}" -n cicd-devsec-ops
```
- RHACS
- GITEA WEBHOOK SECRET
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gitea-bot-token
  namespace: cicd-devsec-ops
type: Opaque
stringData:
  token: CHANGE_ME
```
- GITEA TOKEN
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cicd-devsec-ops-githook-secret
  namespace: cicd-devsec-ops
type: Opaque
stringData:
  GIT_HOOK_SECRET: CHANGE_ME
```
- Cosign key
```shell
cosign generate-key-pair k8s://openshift-pipelines/signing-secrets
```

## Configure the cicd chain

Create the argoCD chain project
```shell
oc apply -f gitops/argocd/project.yaml
```

Create the argoCD Application
```shell
oc apply -f gitops/argocd/application.yaml
```
