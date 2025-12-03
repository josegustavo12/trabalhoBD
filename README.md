# Sistema de Ônibus - Banco de Dados

## Como executar?

```bash
python3 run.py
```

O script inicia automaticamente 2 containers Docker:
- **sistemaonibus_db** - PostgreSQL na porta 5433
- **sistemaonibus_app** - Aplicação Python

## Possiveis problemas
Caso fique muito tempo conectando o BD, provavelmente é erro de conexão entre o container que roda a interface do terminal e o container do Postgree, a solução é:
```bash
docker compose down
```
e rodar novamente o 

```bash
python3 run.py
```

## Usuários de Teste

O sistema inicia com usuários já cadastrados. Para ver todos os usuários, senhas e dados disponíveis:

1. Execute o sistema
2. No menu principal, selecione **"Informações para DEBUG"**
3. Veja a lista completa de cidadãos, gestores, linhas e bairros

### Exemplos de Login

**Cidadão:**
- Email: `maria.santos@test.com`
- Senha: `senha123`

**Gestor:**
- Email: `ricardo.mendes@test.com`
- Senha: `gestor123`

## Comandos Úteis

```bash
# Parar containers
docker compose down

# Ver logs
docker compose logs

# Reiniciar do zero 
docker compose down -v
python3 run.py
```

## Credenciais do Banco

```
Host: localhost
Port: 5433
Database: sistemaonibus
User: app_user
Password: trabalhobd
``` 