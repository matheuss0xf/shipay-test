# Shipay Back-end Challenge
---

#### Tarefa 1: 
```sql
SELECT u.name, u.email, r.description AS role_description, c.description AS claim_description
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN user_claims uc ON u.id = uc.user_id
JOIN claims c ON uc.claim_id = c.id;
```
![image.png](image1.png)

#### Tarefa 2: 

```sql
session.execute(
    select(
        User.name.label('user_name'),
        User.email.label('user_email'),
        Role.description.label('role_description'),
        func.string_agg(Claim.description, ', ').label('claim_descriptions'),
    )
    .join(Role, User.role_id == Role.id)
    .join(UserClaim, User.id == UserClaim.user_id)
    .join(Claim, UserClaim.claim_id == Claim.id)
    .group_by(User.id, Role.description)
)
```

![image.png](image.png)

## Pré-requisitos
---
Antes de executar o projeto, certifique-se de ter os seguintes requisitos instalados em seu ambiente de desenvolvimento:

- Python 3.10 ou superior
- pipenv (gerenciador de pacotes do Python)
- PostgreSQL

## Configuração do ambiente
---
1. Clone o repositório do projeto:
```bash
git clone https://github.com/matheuss0xf/backend-challenge.git
```

2. Acesse o diretório do projeto:
```bash
cd backend-challenge/api
```

3. Instale as dependências do projeto:
```bash
pipenv install
```

4. Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis de ambiente:
```bash
DATABASE_URL=postgresql://shipay:shipay123@127.0.0.1:5432/backend_challenge
```

5. Ative o ambiente virtual do projeto:
```bash
pipenv shell
```

6. Inicie o banco de dados e a aplicação:
```bash
docker compose up -d
```

7. Crie e aplique as migrações do banco de dados:
```bash
alembic upgrade head
```

8. Execute a aplicação:
```bash
task run
```

--- 

## Deploy da aplicação google cloud
---

```yaml
steps:
  # Etapa 1: Construir a imagem Docker e marcar com o SHA do commit
  - name: gcr.io/cloud-builders/docker
    id: Build Cloud Run
    args:
      - build
      - "--no-cache"
      - "-t"
      - "$_GCR_HOSTNAME/$PROJECT_ID/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA"  # Imagem com tag do commit
      - .  # Diretório onde está o Dockerfile
      - "-f"
      - Dockerfile

  # Etapa 2: Enviar a imagem para o Google Container Registry
  - name: gcr.io/cloud-builders/docker
    id: Push Image
    args:
      - push
      - "$_GCR_HOSTNAME/$PROJECT_ID/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA"

  # Etapa 3: Fazer deploy da imagem no Cloud Run
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk:slim"
    id: Deploy Cloud Run Image
    args:
      - -c
      - |
        gcloud run deploy $_SERVICE_NAME \
          --image='$_GCR_HOSTNAME/$PROJECT_ID/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA' \
          --set-secrets='DATABASE_URL=DATABASE_URL:latest'  # Configuração de variáveis secretas
          --service-account='$_SERVICE_NAME@$PROJECT_ID.iam.gserviceaccount.com' \
          --no-allow-unauthenticated \  # Somente usuários autenticados podem acessar
          --region=$_DEPLOY_REGION  \
          --platform=$_PLATFORM \
          --min-instances=0 \  # Escalabilidade: mínimo de instâncias
          --max-instances=2 \  # Escalabilidade: máximo de instâncias
          --concurrency=1000 \  # Número máximo de requisições simultâneas por instância
          --memory=512Mi \  # Memória por instância
          --cpu=2 \  # CPUs por instância
          --port=$_PORT
    entrypoint: bash

  # Etapa 4: Criar configuração do API Gateway
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk:slim"
    id: Create API Gateway Config
    args:
      - "-c"
      - |
        apt-get update
        apt-get install -qq -y gettext

        # Substituir variáveis no arquivo OpenAPI
        export APP_ADDRESS=$(gcloud run services describe $_SERVICE_NAME    --region $_DEPLOY_REGION --format 'value(status.url)')
        export API_HOSTNAME=$(gcloud api-gateway apis describe $_SERVICE_NAME --format 'value(managedService)')

        # Substituindo variáveis no arquivo OpenAPI
        envsubst '$API_HOSTNAME' < openapi-serveless.yaml > openapi-serveless-step1.yaml
        envsubst '$APP_ADDRESS' < openapi-serveless-step1.yaml > openapi-serveless-step2.yaml
        cp openapi-serveless-step2.yaml /workspace/openapi-serveless.yaml

        # Criar configuração do API Gateway
        gcloud api-gateway api-configs create $_SERVICE_NAME-$COMMIT_SHA  \
          --api=$_SERVICE_NAME  \
          --backend-auth-service-account='$_SERVICE_NAME@$PROJECT_ID.iam.gserviceaccount.com' \
          --openapi-spec=/workspace/openapi-serveless.yaml
    entrypoint: bash

  # Etapa 5: Deploy da configuração do API Gateway
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk:slim"
    id: Deploy API Gateway
    args:
      - api-gateway
      - gateways
      - update
      - "$_SERVICE_NAME"
      - "--api=$_SERVICE_NAME"
      - "--api-config=$_SERVICE_NAME-$COMMIT_SHA"
      - "--location=$_DEPLOY_REGION"
    entrypoint: gcloud

images:
  - "$_GCR_HOSTNAME/$PROJECT_ID/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA"  # Definição da imagem a ser enviada

options:
  substitutionOption: ALLOW_LOOSE
  logging: CLOUD_LOGGING_ONLY  # Logs de execução no Google Cloud

substitutions:
  _GCR_HOSTNAME: us.gcr.io  # Host do Google Container Registry
  _SERVICE_NAME: api  # Nome do serviço
  _DEPLOY_REGION: us-central1  # Região do deploy
  _PLATFORM: managed  # Plataforma gerenciada no Cloud Run
  _PORT: "80"  # Porta do serviço
  _TRIGGER_ID: 149fb547-66de-458e-9914-8ffcd9b166b7  # ID do trigger de CI/CD
  _LABELS: gcb-trigger-id=149fb547-66de-458e-9914-8ffcd9b166b7  # Labels para controle

tags:
  - gcp-cloud-build-deploy-cloud-run  # Tags de identificação do processo
  - gcp-cloud-build-deploy-cloud-run-managed
  - api  # Tags de relevância para o serviço

```
Obs: Não vai funcionar, pois é necessário criar o arquivo openapi-serverless.yaml, mas é nesse caminho para fazer o deploy para o Google Cloud. Também poderia criar uma GitHub Action para automatizar esse processo, o que ficaria sensacional.

#### Tarefa 6:

O erro de AttributeError indica que o código está tentando acessar um atributo chamado WALLET_X_TOKEN_MAX_AGE dentro do módulo core.settings, mas esse atributo não está presente ou não foi corretamente definido no arquivo de configurações.

Verifique as configurações de ambiente e certifique-se de que o valor da variável foi definido corretamente.

#### Tarefa 7:

- Remover o logging do `Pipfile`, já que o logging é uma função built-in do Python.
- Como é um script, atualizaria para a versão mais recente do Python, que traz diversas melhorias.
- Melhoraria os nomes das variáveis, tornando-os mais objetivos. Por exemplo: “var1” — o que seria isso? Perdemos muito tempo tentando entender nomes de variáveis mal definidos.
- Removeria a string de conexão do código. Mesmo que o repositório seja privado, colocaria a informação em um arquivo `.env` e aplicaria um dotenv.
- Armazenaria a senha do usuário de forma criptografada ou, idealmente, não a armazenaria no monitoramento. Dados sensíveis não devem ser utilizados além do login e senha iniciais; após isso, para manter a sessão, deve-se usar um refresh token.
- A tratativa de erros em scripts é essencial, então aplicaria um bloco `try/except`.
- Usar `with` para abrir arquivos é uma boa prática pois garante que os recursos sejam liberados após ser utilizado.
- Pode deixar o código mais modular, fazendo que ele tenha funções menores com responsabilidades bem definidas.
- O que será feito com os arquivos Excel após um certo período? Serão excluídos ou continuarão armazenados?

#### Tarefa 8:

Eu utilizaria o **Adapter Pattern** por ser fácil de aplicar e muito eficaz para integrar diferentes interfaces de serviço. Com isso, criaria um adaptador responsável por estabelecer uma interface comum e abstrair as particularidades de cada provedor.

No entanto, o **Factory Pattern** também seria uma boa escolha, especialmente quando precisamos lidar com diferentes provedores de e-mail, SMS, etc., e queremos centralizar a lógica de criação dessas instâncias. O Factory ajuda a decidir qual classe (ou provedor) será instanciada de acordo com as configurações ou parâmetros fornecidos, o que torna a implementação mais flexível e fácil de manter.