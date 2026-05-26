# GitHub Workflows

Zwei Workflows, kein PR-Zwang:

| Workflow | Trigger | Ziel |
|---|---|---|
| `deploy-dev.yml` | Push auf `main` (oder manuell) | Azure Container App **Dev** |
| `deploy-prod.yml` | Nur manuell (`workflow_dispatch`) | Azure Container App **Prod** |

## Flow

1. Commit auf `main` → `deploy-dev.yml` läuft automatisch:
   Odoo-Tests → Image bauen → ACR pushen (`<sha>` + `dev-latest`) → Dev updaten.
2. Wenn Dev passt: Actions → **Deploy Prod** → *Run workflow*.
   Default-Input ist `dev-latest`; alternativ ein konkreter `<sha>`-Tag.
   Der Tag wird in ACR zusätzlich auf `prod-latest` gemappt und auf
   die Prod-Container-App ausgerollt.

## Benötigte Secrets (Repo- oder Org-Level)

| Secret | Inhalt |
|---|---|
| `AZURE_CREDENTIALS` | Service-Principal JSON für `azure/login` (`az ad sp create-for-rbac --sdk-auth`) |
| `ACR_LOGIN_SERVER` | z. B. `fastlogwms.azurecr.io` |
| `AZURE_RESOURCE_GROUP` | Name der Resource Group |
| `AZURE_CONTAINERAPP_DEV` | Name der Dev-Container-App |
| `AZURE_CONTAINERAPP_PROD` | Name der Prod-Container-App |

Der Service Principal braucht:

- `AcrPush` auf das ACR (für `az acr login`, `az acr import`)
- `Contributor` (oder feiner: `Container Apps Contributor`) auf die
  beiden Container Apps bzw. deren Resource Group

## Environments

Beide Deploy-Jobs nutzen GitHub-Environments (`dev`, `prod`).
Wenn ihr später doch noch eine Freigabe vor Prod wollt, lässt sich
das im Environment `prod` via *Required reviewers* aktivieren –
ohne den Workflow zu ändern.
