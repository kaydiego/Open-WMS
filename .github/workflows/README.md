# GitHub Workflow

Ein einziger Workflow, weil das Setup nur fuer Tests ist – keine Prod.

`deploy.yml` triggert bei Push auf `main` (oder manuell):

1. Odoo-Tests gegen Postgres-Service-Container
2. Image bauen, in ACR pushen (`<sha>` + `latest`)
3. Azure Container App per `az containerapp update` auf den neuen Tag setzen

## Benoetigte Repo-Secrets

| Secret | Inhalt |
|---|---|
| `AZURE_CREDENTIALS` | Service-Principal JSON (`az ad sp create-for-rbac --sdk-auth`) |
| `ACR_LOGIN_SERVER` | z. B. `fastlogwms.azurecr.io` |
| `AZURE_RESOURCE_GROUP` | Name der Resource Group |
| `AZURE_CONTAINERAPP` | Name der Container App |

Der Service Principal braucht `AcrPush` auf das ACR und `Contributor`
(oder `Container Apps Contributor`) auf die Resource Group bzw. die App.
Die Container App selber zieht das Image am sinnvollsten via
System-Assigned Identity mit `AcrPull`-Rolle.
