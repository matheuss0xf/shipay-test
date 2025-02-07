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
...

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
