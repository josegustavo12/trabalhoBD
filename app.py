import psycopg2

# Função para abrir conexão com o banco

def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="sistemaonibus",
            user="app_user",
            password="trabalhobd"  # sua senha
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco:", e)
        return None



# INSERÇÕES

# Inserção: cadastrar um novo cidadão (USUARIO + USUARIO_CIDADAO)
def cadastrar_cidadao(conn):
    print("\n=== Cadastro de Cidadão ===")
    cpf = input("CPF (11 dígitos, só números): ").strip()
    rua = input("Rua: ")
    bairro = input("Bairro: ")
    numero = input("Número: ")
    cep = input("CEP (8 dígitos, só números): ").strip()
    email = input("E-mail: ")
    senha = input("Senha: ")

    # status fixo 'A' (ativo)
    status = 'A'

    try:
        with conn.cursor() as cur:
            # Inserir na tabela USUARIO
            cur.execute(
                """
                INSERT INTO USUARIO (CPF, TIPO)
                VALUES (%s, 'C')
                """,
                (cpf,)
            )

            # Inserir na tabela USUARIO_CIDADAO
            numero_int = int(numero) if numero != "" else None

            cur.execute(
                """
                INSERT INTO USUARIO_CIDADAO
                    (CPF, RUA, BAIRRO, NUMERO, CEP, STATUS, EMAIL, SENHA)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (cpf, rua, bairro, numero_int, cep, status, email, senha)
            )

        conn.commit()
        print("Cidadão cadastrado com sucesso!")
    except psycopg2.IntegrityError:
        conn.rollback()
        print("Já existe um usuário com esse CPF ou há problema de integridade.")
    except Exception as e:
        conn.rollback()
        print("Erro ao cadastrar cidadão:", e)


# Inserção: cadastrar um novo gestor (USUARIO + USUARIO_GESTOR)
def cadastrar_gestor(conn):
    print("\n=== Cadastro de Gestor ===")
    cpf = input("CPF (11 dígitos, só números): ").strip()
    rua = input("Rua: ")
    bairro = input("Bairro: ")
    numero = input("Número: ")
    cep = input("CEP (8 dígitos, só números): ").strip()
    cargo = input("Cargo: ")
    email = input("E-mail: ")
    senha = input("Senha: ")
    cnpj_orgao = input("CNPJ do órgão público (14 dígitos): ").strip()

    try:
        with conn.cursor() as cur:
            # Inserir na tabela USUARIO
            cur.execute(
                """
                INSERT INTO USUARIO (CPF, TIPO)
                VALUES (%s, 'G')
                """,
                (cpf,)
            )

            # Inserir na tabela USUARIO_GESTOR
            numero_int = int(numero) if numero != "" else None

            cur.execute(
                """
                INSERT INTO USUARIO_GESTOR
                    (CPF, RUA, BAIRRO, NUMERO, CEP, CARGO, EMAIL, SENHA, CNPJ_ORGAO_PUBLICO)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (cpf, rua, bairro, numero_int, cep, cargo, email, senha, cnpj_orgao)
            )

        conn.commit()
        print("Gestor cadastrado com sucesso!")
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Erro de integridade (CPF ou CNPJ inválido/duplicado):", e)
    except Exception as e:
        conn.rollback()
        print("Erro ao cadastrar gestor:", e)


# CONSULTAS PARA CIDADÃO

# Consulta: listar viagens de um cidadão
def listar_viagens_por_cpf(conn, cpf=None):
    if cpf is None:
        print("\n=== Consultar viagens por CPF ===")
        cpf = input("CPF (11 dígitos, só números): ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    v.DATAHORA_INICIO,
                    v.DATAHORA_FINAL,
                    v.CUSTO_TOTAL,
                    v.NOME_CODIGO_LINHA_EMBARQUE,
                    v.NRO_PARADA_EMBARQUE,
                    v.NOME_CODIGO_LINHA_DESEMBARQUE,
                    v.NRO_PARADA_DESEMBARQUE,
                    o.PLACA,
                    l.TARIFA
                FROM VIAGEM v
                JOIN ONIBUS o
                  ON v.PLACA_ONIBUS = o.PLACA
                JOIN LINHA l
                  ON v.NOME_CODIGO_LINHA_EMBARQUE = l.NOME_CODIGO
                WHERE v.CPF_CIDADAO = %s
                ORDER BY v.DATAHORA_INICIO;
                """,
                (cpf,)
            )

            rows = cur.fetchall()

            if not rows:
                print("Nenhuma viagem encontrada para esse CPF.")
                return

            print(f"\nViagens do CPF {cpf}:")
            for row in rows:
                (data_inicio, data_fim, custo,
                 linha_emb, parada_emb,
                 linha_des, parada_des,
                 placa, tarifa) = row
                print("-" * 60)
                print(f"Início:   {data_inicio}")
                print(f"Fim:      {data_fim}")
                print(f"Linha (embarque):    {linha_emb}  - parada {parada_emb}")
                print(f"Linha (desembarque): {linha_des} - parada {parada_des}")
                print(f"Placa do ônibus:     {placa}")
                print(f"Tarifa da linha:     R$ {tarifa}")
                print(f"Custo total:         R$ {custo}")
            print("-" * 60)

    except Exception as e:
        print("Erro ao consultar viagens:", e)


# Consulta: total gasto em viagens por um cidadão
def total_gasto_por_cidadao(conn, cpf):
    """Mostra o total gasto em viagens por um cidadão."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(SUM(CUSTO_TOTAL), 0)
                FROM VIAGEM
                WHERE CPF_CIDADAO = %s
                """,
                (cpf,)
            )
            (total,) = cur.fetchone()
            print(f"\nTotal gasto em viagens pelo CPF {cpf}: R$ {total}")
    except Exception as e:
        print("Erro ao calcular total gasto:", e)


# Consulta: linhas disponíveis em uma região (bairro)
def consultar_linhas_disponiveis(conn):
    print("\n=== Linhas disponíveis por bairro ===")
    bairro = input("Informe o bairro: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT
                    l.NOME_CODIGO,
                    l.TARIFA,
                    l.TEMPO_PERCURSO,
                    e.NOME AS nome_empresa
                FROM LINHA l
                JOIN PONTO_PARADA p
                  ON p.NOME_CODIGO_LINHA = l.NOME_CODIGO
                JOIN EMPRESA_PUBLICA e
                  ON l.CNPJ_EMPRESA_PUBLICA = e.CNPJ
                WHERE p.BAIRRO ILIKE %s
                  AND l.ATIVO = 'S'
                ORDER BY l.NOME_CODIGO;
                """,
                (bairro,)
            )
            rows = cur.fetchall()
            if not rows:
                print("Nenhuma linha encontrada para esse bairro.")
                return
            print(f"\nLinhas que atendem o bairro {bairro}:")
            for nome_codigo, tarifa, tempo, empresa in rows:
                print("-" * 60)
                print(f"Linha:   {nome_codigo}")
                print(f"Tarifa:  R$ {tarifa}")
                print(f"Tempo:   {tempo} minutos")
                print(f"Empresa: {empresa}")
            print("-" * 60)
    except Exception as e:
        print("Erro ao consultar linhas disponíveis:", e)


# Consulta: pontos de parada próximos a uma localização (bairro + rua)
def consultar_pontos_parada(conn):
    print("\n=== Pontos de parada por localização ===")
    bairro = input("Informe o bairro: ").strip()
    rua = input("Informe o nome completo da rua: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.NOME_CODIGO_LINHA,
                    p.NRO_PARADA,
                    p.RUA,
                    p.BAIRRO,
                    p.NUMERO,
                    p.CEP,
                    p.PRESENCA_COBERTURA,
                    p.EH_ORIGEM,
                    p.EH_DESTINO
                FROM PONTO_PARADA p
                WHERE p.BAIRRO ILIKE %s
                  AND p.RUA    ILIKE %s
                ORDER BY p.NOME_CODIGO_LINHA, p.NRO_PARADA;
                """,
                (bairro, rua)
            )
            rows = cur.fetchall()
            if not rows:
                print("Nenhum ponto de parada encontrado para essa localização.")
                return
            print(f"\nPontos de parada em {rua} - {bairro}:")
            for (linha, nro_parada, rua_p, bairro_p,
                 numero, cep, cobertura, eh_origem, eh_destino) in rows:
                print("-" * 60)
                print(f"Linha:          {linha}")
                print(f"Nro parada:     {nro_parada}")
                print(f"Endereço:       {rua_p}, {numero} - {bairro_p}")
                print(f"CEP:            {cep}")
                print(f"Cobertura:      {cobertura}")
                print(f"É origem?       {eh_origem}")
                print(f"É destino?      {eh_destino}")
            print("-" * 60)
    except Exception as e:
        print("Erro ao consultar pontos de parada:", e)


# CONSULTAS PARA GESTOR (e alguns relatórios gerais)

# Consulta: listar todas as linhas ativas e sua empresa pública
def listar_linhas_ativas(conn):
    """Lista todas as linhas ativas e sua empresa pública."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    l.NOME_CODIGO,
                    l.TARIFA,
                    l.TEMPO_PERCURSO,
                    e.NOME AS nome_empresa
                FROM LINHA l
                JOIN EMPRESA_PUBLICA e
                  ON l.CNPJ_EMPRESA_PUBLICA = e.CNPJ
                WHERE l.ATIVO = 'S'
                ORDER BY l.NOME_CODIGO;
                """
            )
            rows = cur.fetchall()
            if not rows:
                print("Nenhuma linha ativa encontrada.")
                return
            print("\n=== Linhas ativas ===")
            for nome_codigo, tarifa, tempo, empresa in rows:
                print("-" * 60)
                print(f"Linha:   {nome_codigo}")
                print(f"Tarifa:  R$ {tarifa}")
                print(f"Tempo:   {tempo} minutos")
                print(f"Empresa: {empresa}")
            print("-" * 60)
    except Exception as e:
        print("Erro ao listar linhas ativas:", e)


# Consulta: quantidade de viagens por linha de embarque
def viagens_por_linha(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    v.NOME_CODIGO_LINHA_EMBARQUE AS linha,
                    COUNT(*) AS qtd_viagens
                FROM VIAGEM v
                GROUP BY v.NOME_CODIGO_LINHA_EMBARQUE
                ORDER BY qtd_viagens DESC;
                """
            )
            rows = cur.fetchall()
            if not rows:
                print("Nenhuma viagem registrada.")
                return
            print("\n=== Quantidade de viagens por linha de embarque ===")
            for linha, qtd in rows:
                print(f"Linha {linha}: {qtd} viagens")
    except Exception as e:
        print("Erro ao listar viagens por linha:", e)


# NOVA Consulta: Rotas mais utilizadas entre bairros (origem x destino)
def rotas_mais_utilizadas(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    pe.BAIRRO AS bairro_origem,
                    pd.BAIRRO AS bairro_destino,
                    COUNT(*) AS qtd_viagens
                FROM VIAGEM v
                JOIN PONTO_PARADA pe
                  ON v.NOME_CODIGO_LINHA_EMBARQUE = pe.NOME_CODIGO_LINHA
                 AND v.NRO_PARADA_EMBARQUE        = pe.NRO_PARADA
                JOIN PONTO_PARADA pd
                  ON v.NOME_CODIGO_LINHA_DESEMBARQUE = pd.NOME_CODIGO_LINHA
                 AND v.NRO_PARADA_DESEMBARQUE        = pd.NRO_PARADA
                WHERE pe.BAIRRO IS NOT NULL
                  AND pd.BAIRRO IS NOT NULL
                GROUP BY bairro_origem, bairro_destino
                ORDER BY qtd_viagens DESC;
                """
            )
            rows = cur.fetchall()
            if not rows:
                print("Nenhuma rota registrada.")
                return
            print("\n=== Rotas mais utilizadas entre bairros (origem → destino) ===")
            for origem, destino, qtd in rows:
                print(f"{origem} → {destino}: {qtd} viagens")
    except Exception as e:
        print("Erro ao listar rotas mais utilizadas:", e)


# NOVA Consulta: Horários de pico (por hora do dia)
def horarios_de_pico(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    EXTRACT(HOUR FROM DATAHORA_INICIO) AS hora_do_dia,
                    COUNT(*) AS qtd_viagens
                FROM VIAGEM
                GROUP BY hora_do_dia
                ORDER BY qtd_viagens DESC;
                """
            )
            rows = cur.fetchall()
            if not rows:
                print("Nenhuma viagem registrada.")
                return
            print("\n=== Horários de pico (por hora do dia) ===")
            for hora, qtd in rows:
                print(f"{int(hora):02d}h: {qtd} viagens")
    except Exception as e:
        print("Erro ao listar horários de pico:", e)


# LOGIN + SUBMENUS

# LOGIN CIDADÃO
def entrar_como_cidadao(conn):
    print("\n=== Login Cidadão ===")
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()

    try:
        with conn.cursor() as cur:
            # busca do CPF a partir do email/senha
            cur.execute(
                """
                SELECT CPF
                FROM USUARIO_CIDADAO
                WHERE EMAIL = %s AND SENHA = %s
                """,
                (email, senha)
            )
            result = cur.fetchone()

        if not result:
            print("Email ou senha de cidadão inválidos.")
            return

        cpf = result[0]
        print(f"Login de cidadão bem-sucedido! (CPF {cpf})")
        menu_cidadao(conn, cpf)

    except Exception as e:
        print("Erro ao fazer login de cidadão:", e)


# MENU DO CIDADÃO
def menu_cidadao(conn, cpf):
    while True:
        print("\n------ Menu do Cidadão ------")
        print("1 - Listar minhas viagens")
        print("2 - Ver total gasto em viagens")
        print("3 - Consultar linhas disponíveis por bairro")
        print("4 - Consultar pontos de parada por localização")
        print("0 - Voltar ao menu principal")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_viagens_por_cpf(conn, cpf)
        elif opcao == "2":
            total_gasto_por_cidadao(conn, cpf)
        elif opcao == "3":
            consultar_linhas_disponiveis(conn)
        elif opcao == "4":
            consultar_pontos_parada(conn)
        elif opcao == "0":
            break
        else:
            print("Opção inválida, tente novamente.")


# LOGIN GESTOR
def entrar_como_gestor(conn):
    print("\n=== Login Gestor ===")
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM USUARIO_GESTOR
                WHERE EMAIL = %s AND SENHA = %s
                """,
                (email, senha)
            )
            result = cur.fetchone()

        if not result:
            print("Email ou senha de gestor inválidos.")
            return

        print(f"Login de gestor bem-sucedido! (Email {email})")
        menu_gestor(conn, email)

    except Exception as e:
        print("Erro ao fazer login de gestor:", e)


# MENU DO GESTOR
def menu_gestor(conn, email):
    while True:
        print("\n------ Menu do Gestor ------")
        print("1 - Listar linhas ativas")
        print("2 - Ver quantidade de viagens por linha")
        print("3 - Ver rotas mais utilizadas entre bairros")
        print("4 - Ver horários de pico do sistema")
        print("0 - Voltar ao menu principal")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_linhas_ativas(conn)
        elif opcao == "2":
            viagens_por_linha(conn)
        elif opcao == "3":
            rotas_mais_utilizadas(conn)
        elif opcao == "4":
            horarios_de_pico(conn)
        elif opcao == "0":
            break
        else:
            print("Opção inválida, tente novamente.")


# MENU PRINCIPAL

def main():
    conn = get_connection()
    if not conn:
        print("Não foi possível conectar ao banco. Encerrando.")
        return

    while True:
        print("\n================= SISTEMA DE ÔNIBUS =================")
        print("1 - Cadastrar novo cidadão")
        print("2 - Cadastrar novo gestor")
        print("3 - Entrar como cidadão")
        print("4 - Entrar como gestor")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_cidadao(conn)
        elif opcao == "2":
            cadastrar_gestor(conn)
        elif opcao == "3":
            entrar_como_cidadao(conn)
        elif opcao == "4":
            entrar_como_gestor(conn)
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")

    conn.close()


if __name__ == "__main__":
    main()
