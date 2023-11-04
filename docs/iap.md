# Add Identity-Aware Proxy

Website use [Identity-Aware Proxy (IAP)](https://cloud.google.com/iap) to guard
access. Non public instances are guarded by IAP.

To give user access to the website, need to have "IAP-secured Web App User" role
which can be added by following [this](https://cloud.google.com/iap/docs/enabling-kubernetes-howto#iap-access).

## Add IAP to a GKE deployment

Most of the steps here is from IAP [documentation](https://cloud.google.com/iap/docs/enabling-kubernetes-howto).
This lists a concrete steps to aid quick setup.

### Set GKE context

```bash
export PROJECT_ID=<PROJECT_ID>
export REGION=<GKE_REGION>
export CLUSTER_NAME=website-$REGION
gcloud config set project $PROJECT_ID
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION
```

### Configure the OAuth consent screen

Follow [documentation](https://cloud.google.com/iap/docs/enabling-kubernetes-howto#oauth-configure)

### Create OAuth credential

Follow [documentation](https://cloud.google.com/iap/docs/enabling-kubernetes-howto#oauth-credentials)

### Setup IAP access

Follow [documentation](https://cloud.google.com/iap/docs/enabling-kubernetes-howto#iap-access)

### Configure BackendConfig

Create a kubenetest secret, replace `client_id_key` and `client_secret_key` with
the actual key from OAuth setup.

```bash
kubectl create secret generic iap-secret --from-literal=client_id=[client_id_key] \
    --from-literal=client_secret=[client_secret_key] -n website
```

Deploy backend config and service

```bash
# In <REPO_ROOT>/gke
kubectl apply -f backendconfig_iap.yaml
kubectl apply -f mcs.yaml

cp mci.yaml.tpl mci.yaml
# Update <IP> to be the static IP of the website, which can be found in
# <REPO_ROOT>/deploy/gke/<ENV>.yaml,
# [Optional] change the certificate to match the current SSL certificate
kubectl apply -f mci.yaml
```

Verfify backend config

```bash
kubectl -n website -ojson get backendconfig | grep '"iap":' -C 5
```

### Verify IAP

IAP takes effect in a few minutes. To verify, access the web page in an in-cognito browser page, a Google auth windown would appear with the configured consent screen
from the step above.

## Allow Programtic Access

To allow webdriver tests to access website protected by IAP, follow the steps in
[IAP Programmatic
Authentication](https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_service_account).
In summary with the following steps:

Create a SETTING_FILE:

```txt
access_settings:
  oauth_settings:
    programmatic_clients: ["<CLIENT_ID>"]
```

Share Oauth Client

```bash
export PROJECT_ID=<YOUR_PROJECT_ID>
gcloud iap settings set SETTING_FILE --project=$PROJECT_ID --resource-type=iap_web
```
