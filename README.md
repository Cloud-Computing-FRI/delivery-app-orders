Microservice for placing and tracking customer orders: order lifecycle, status updates, and order history.

## CI/CD

A push to `main` deploys to staging, and an approved manual run deploys to prod
(`.github/workflows/ci-cd.yml`). The required GitHub secrets, how to retrieve
them with the Azure CLI, and how to manage the cluster with `kubectl` live on the
organization profile:
https://github.com/Cloud-Computing-FRI/.github

The workflow logs in to Azure with
OIDC under the subject
`repo:Cloud-Computing-FRI/delivery-app-orders:environment:<staging|prod>`, and in
prod it reads `DATABASE_URL` from the pre-created `db-orders` Secret.
