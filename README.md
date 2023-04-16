# cicd-e2e-lab-deploy

This repo contains the material to deploy a cicd chain on openshift.


## Deploy ArgoCD, cluster-wide subscriptions and create namespaces

```shell
oc apply -f gitops/sub.yaml
oc apply -f gitops/ns.yaml
oc apply -f gitops/ClusterRoleBinding.yaml 
```

## Quay configuration and credentials setup

In quay.io create a public repository, that will be used to store the image build by the pipeline.
Update the file ./cicd-devsec-ops/gitops/base/pipeline/02_trigger-template.yaml to use the url of your new targeted repo instead of the default one.

![create repo](images/create-repo.png)

Then create a robot accound that will be used by the pipeline service account in openshift.

Click on your username on the top left > Account settings > Robot Accounts > Create Robot Account > Provide a name for your bot > select the repo that we have create in the previous step > Select admin permission. 

Then click on Robot Account and Download credentials config


```shell
export QUAY_TOKEN="XXX"
export EMAIL="XXX"
export USERNAME="feven+acs_integration"
export NAMESPACE="cicd-devsec-ops"
```

Create a namespace and the secret for the registry

```shell
oc create secret generic registry-credentials --from-file=config.json -n ${NAMESPACE}
```

Replace ROOT_URL with your correct base domain in :
```shell
./cicd-devsec-ops/gitops/base/gitea/gitea-server.yaml
```
And replace GITEA_HOST_URL with your correct base domain :
```shell
./cicd-devsec-ops/gitops/base/pipeline/02_trigger-template.yaml 
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

## Post configuration

### Gitea configuration

At first we need to configure our gitea account and push a repository.

Get the URL for the Gitea route:
GITEA_URL=$(echo "https://$(oc get route gitea -o=jsonpath='{.spec.host}' -n gitea)")

Connect to gitea using gitea and redhat123.

At first we will create an Access Tokens to get access to the gitea API.

On the top right select the gitea icons and click on settings. Then go in applications. Put gitea-bot-token as token name and click on Generate Token.

![create repo](images/gitea-bot-token.png)

Copy the generate token and create the following gitea secret:


```yaml
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: gitea-bot-token
  namespace: cicd-devsec-ops
type: Opaque
stringData:
  token: 43d1db62909b1346e34a95a48d1256498c2b108e
EOF
```

Now on the top right click on the + and click on New repository. Give python-app as name, and keep other default parameters. Click on Create Repository. 

Then click on settings > Collaborators and add Developer Collaborator with Administrator right.

![create repo](images/add-developer.png)

Then clone the following repo https://github.com/adrien-legros/openshift-pipelines-demo and change the remote origin
git remote set-url origin $GITEA_URL/gitea/python-app.git 



Patch the service account to get access to the creds

- Patch build-bot
```shell
oc patch serviceaccount build-bot \
  -p "{\"imagePullSecrets\": [{\"name\": \"registry-credentials\"}]}" -n ${NAMESPACE}
```

- GITEA TOKEN

```yaml
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: cicd-devsec-ops-githook-secret
  namespace: cicd-devsec-ops
type: Opaque
stringData:
  GIT_HOOK_SECRET: $(echo $RANDOM | md5sum | cut -d" " -f1)
EOF
```

Get the GIT_HOOK_SECRET Genereated.



Create webhook. Click on your application then go on setting > Webhooks and click on add Webhook. Then click on Gitea.

In Target url put the url of the event listener and put the git_hook-secret generated previously.

- GITEA TOKEN

```yaml
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: cicd-devsec-ops-githook-secret
  namespace: cicd-devsec-ops
type: Opaque
stringData:
  GIT_HOOK_SECRET: $(echo $RANDOM | md5sum | cut -d" " -f1)
EOF
```


### RHACS configuration

Go in RHACS 

```shell
echo "https://$(oc get route central -o=jsonpath='{.spec.host}' -n rhacs-operator)"
```

Connect using admin as user and get password with the following command:

```shell
oc -n rhacs-operator get secret central-htpasswd -o go-template='{{index .data "password" | base64decode}}'
```

- Cosign key
```shell
cosign generate-key-pair k8s://openshift-pipelines/signing-secrets
```

Go in platform configuration > Integrations and select api token.

Click on Generate Token. Choose a token name and select continuous Integration as Role.
Copy the Api Token Integration and create the integration secret.

```shell
ROX_API_TOKEN=YOURTOKEN
ACS_ROUTE=$(echo "$(oc get route central -o=jsonpath='{.spec.host}' -n rhacs-operator)")
cat > /tmp/roxsecret.yaml << EOF
apiVersion: v1
data:
  rox_api_token: "$(echo $ROX_API_TOKEN | tr -d '\n' | base64 -w 0)"
  rox_central_endpoint: "$(echo $ACS_ROUTE:443 | tr -d '\n' | base64 -w 0)"
kind: Secret
metadata:
  name: rox-api-token
  namespace: ${NAMESPACE}
type: Opaque
EOF

oc apply -f /tmp/roxsecret.yaml
```

Toujours dans ACS passe la policy Fixable Severity at least Important de Enforce a Informative.



Autres:

Remplacer les reference a quay.io/feven par votre registry