import psycopg2
import time
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from pyfiglet import Figlet
import readchar

console = Console()

def validar_cpf(cpf):
    if not cpf:
        return False, "CPF não pode estar vazio"

    if not cpf.isdigit():
        return False, "CPF deve conter apenas números (sem pontos ou traços)"

    if len(cpf) != 11:
        return False, "CPF deve conter exatamente 11 dígitos"

    return True, "CPF válido"

def validar_cep(cep):
    if not cep:
        return False, "CEP não pode estar vazio"

    if not cep.isdigit():
        return False, "CEP deve conter apenas números (sem pontos ou traços)"

    if len(cep) != 8:
        return False, "CEP deve conter exatamente 8 dígitos"

    return True, "CEP válido"

def validar_email(email):
    if not email:
        return False, "Email não pode estar vazio"

    if '@' not in email:
        return False, "Email deve conter o caractere @"

    partes = email.split('@')
    if len(partes) != 2 or not partes[0] or not partes[1]:
        return False, "Email deve ter o formato nome@dominio"

    return True, "Email válido"

def validar_numero_casa(numero):
    if not numero:
        return True, "Número vazio é válido"

    if not numero.isdigit():
        return False, "Número da casa deve conter apenas dígitos"

    return True, "Número válido"

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def show_loading(message, duration=1):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"[cyan]{message}...", total=None)
        time.sleep(duration)

def show_banner():
    clear_screen()
    f = Figlet(font='slant')
    banner = f.renderText('SISTEMA DE')
    banner2 = f.renderText('   ONIBUS')

    console.print(banner, style="bold cyan")
    console.print(banner2, style="bold yellow")
    console.print("\n[dim]Sistema de Gerenciamento de Transporte Publico[/dim]", justify="center")
    console.print("\n[bold cyan]Equipe de Desenvolvimento[/bold cyan]\n", justify="center")

    team_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2), show_edge=False)
    team_table.add_column(justify="left", style="cyan")
    team_table.add_column(justify="right", style="yellow")

    team_table.add_row("José Gustavo Victor Pinheiro Alencar", "14783765")
    team_table.add_row("Breno Wingeter de Castilho", "15573522")
    team_table.add_row("Manassés Arange de Moura", "15474205")
    team_table.add_row("Carolina Gomes Guerreiro", "15445453")

    console.print(Align.center(team_table))
    console.print()

def get_connection():
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]Conectando ao banco de dados...", total=None)
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5433")),
                database=os.getenv("DB_NAME", "sistemaonibus"),
                user=os.getenv("DB_USER", "app_user"),
                password=os.getenv("DB_PASSWORD", "trabalhobd")
            )
            time.sleep(0.5)
        console.print("[green]Conexao estabelecida com sucesso![/green]\n")
        time.sleep(0.5)
        return conn
    except Exception as e:
        console.print(f"[red]Erro ao conectar ao banco:[/red] {e}\n")
        return None

def menu_select(title, options, description=None):
    selected = 0

    while True:
        clear_screen()
        show_banner()

        if description:
            console.print(Panel(description, style="cyan", box=box.ROUNDED))
            console.print()

        console.print(f"[bold cyan]=== {title} ===[/bold cyan]\n")

        for i, option in enumerate(options):
            if i == selected:
                console.print(f"  [black on cyan]> {option}[/black on cyan]")
            else:
                console.print(f"    {option}")

        console.print("\n[dim]Use setas para navegar, Enter para selecionar[/dim]")

        key = readchar.readkey()

        if key == readchar.key.UP and selected > 0:
            selected -= 1
        elif key == readchar.key.DOWN and selected < len(options) - 1:
            selected += 1
        elif key == readchar.key.ENTER or key == '\r' or key == '\n':
            return selected

# INFORMACOES DEBUG
def mostrar_info_debug(conn):
    clear_screen()
    show_banner()

    console.print(Panel.fit(
        "[bold yellow]Informacoes para DEBUG[/bold yellow]",
        border_style="yellow"
    ))
    console.print()

    try:
        # Usuarios Cidadao
        with conn.cursor() as cur:
            cur.execute("""
                SELECT uc.EMAIL, uc.SENHA, uc.CPF, uc.STATUS
                FROM USUARIO_CIDADAO uc
                ORDER BY uc.EMAIL
            """)
            cidadaos = cur.fetchall()

        if cidadaos:
            table = Table(title="USUARIOS CIDADAO",
                        title_style="bold cyan",
                        box=box.ROUNDED,
                        border_style="cyan")

            table.add_column("Email", style="cyan")
            table.add_column("Senha", style="yellow")
            table.add_column("CPF", style="white")
            table.add_column("Status", style="green", justify="center")

            for email, senha, cpf, status in cidadaos:
                table.add_row(email, senha, cpf, "Ativo" if status == 'A' else "Inativo")

            console.print(table)
            console.print()

        # Usuarios Gestor
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ug.EMAIL, ug.SENHA, ug.CPF, ug.CARGO
                FROM USUARIO_GESTOR ug
                ORDER BY ug.EMAIL
            """)
            gestores = cur.fetchall()

        if gestores:
            table = Table(title="USUARIOS GESTOR",
                        title_style="bold yellow",
                        box=box.ROUNDED,
                        border_style="yellow")

            table.add_column("Email", style="yellow")
            table.add_column("Senha", style="cyan")
            table.add_column("CPF", style="white")
            table.add_column("Cargo", style="green")

            for email, senha, cpf, cargo in gestores:
                table.add_row(email, senha, cpf, cargo)

            console.print(table)
            console.print()

        # Linhas e Bairros
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT l.NOME_CODIGO, p.BAIRRO
                FROM LINHA l
                JOIN PONTO_PARADA p ON l.NOME_CODIGO = p.NOME_CODIGO_LINHA
                WHERE l.ATIVO = 'S' AND p.BAIRRO IS NOT NULL
                ORDER BY l.NOME_CODIGO, p.BAIRRO
            """)
            linhas = cur.fetchall()

        if linhas:
            table = Table(title="LINHAS E BAIRROS DISPONIVEIS",
                        title_style="bold green",
                        box=box.ROUNDED,
                        border_style="green")

            table.add_column("Linha", style="cyan")
            table.add_column("Bairro", style="green")

            for linha, bairro in linhas:
                table.add_row(linha, bairro)

            console.print(table)
            console.print()

        # Estatisticas
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM USUARIO_CIDADAO")
            total_cidadaos = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM USUARIO_GESTOR")
            total_gestores = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM VIAGEM")
            total_viagens = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM LINHA WHERE ATIVO = 'S'")
            total_linhas = cur.fetchone()[0]

        stats = Panel(
            f"[cyan]Cidadaos:[/cyan] {total_cidadaos}    "
            f"[yellow]Gestores:[/yellow] {total_gestores}    "
            f"[green]Viagens:[/green] {total_viagens}    "
            f"[blue]Linhas Ativas:[/blue] {total_linhas}",
            title="ESTATISTICAS DO SISTEMA",
            border_style="magenta",
            box=box.DOUBLE
        )
        console.print(stats)

    except Exception as e:
        console.print(f"[red]Erro ao buscar informacoes:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def cadastrar_cidadao(conn):
    clear_screen()
    show_banner()

    console.print(Panel.fit(
        "[bold cyan]Cadastro de Novo Cidadao[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    cpf = Prompt.ask("[cyan]CPF[/cyan] (11 digitos)")

    cpf_valido, mensagem = validar_cpf(cpf)
    if not cpf_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    rua = Prompt.ask("[cyan]Rua[/cyan]")
    bairro = Prompt.ask("[cyan]Bairro[/cyan]")

    numero = Prompt.ask("[cyan]Numero[/cyan]")
    numero_valido, mensagem = validar_numero_casa(numero)
    if not numero_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    cep = Prompt.ask("[cyan]CEP[/cyan] (8 digitos)")
    cep_valido, mensagem = validar_cep(cep)
    if not cep_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    email = Prompt.ask("[cyan]E-mail[/cyan]")
    email_valido, mensagem = validar_email(email)
    if not email_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    senha = Prompt.ask("[cyan]Senha[/cyan]", password=True)

    status = 'A'

    try:
        show_loading("Salvando dados")
        with conn.cursor() as cur:
            cur.execute("INSERT INTO USUARIO (CPF, TIPO) VALUES (%s, 'C')", (cpf,))
            numero_int = int(numero) if numero != "" else None
            cur.execute(
                """INSERT INTO USUARIO_CIDADAO
                   (CPF, RUA, BAIRRO, NUMERO, CEP, STATUS, EMAIL, SENHA)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (cpf, rua, bairro, numero_int, cep, status, email, senha)
            )
        conn.commit()
        console.print("\n[green]Cidadao cadastrado com sucesso![/green]")
    except psycopg2.IntegrityError:
        conn.rollback()
        console.print("\n[red]Ja existe um usuario com esse CPF![/red]")
    except Exception as e:
        conn.rollback()
        console.print(f"\n[red]Erro ao cadastrar:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def cadastrar_gestor(conn):
    clear_screen()
    show_banner()

    console.print(Panel.fit(
        "[bold yellow]Cadastro de Novo Gestor[/bold yellow]",
        border_style="yellow"
    ))
    console.print()

    cpf = Prompt.ask("[yellow]CPF[/yellow] (11 digitos)")

    cpf_valido, mensagem = validar_cpf(cpf)
    if not cpf_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    rua = Prompt.ask("[yellow]Rua[/yellow]")
    bairro = Prompt.ask("[yellow]Bairro[/yellow]")

    numero = Prompt.ask("[yellow]Numero[/yellow]")
    numero_valido, mensagem = validar_numero_casa(numero)
    if not numero_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    cep = Prompt.ask("[yellow]CEP[/yellow] (8 digitos)")
    cep_valido, mensagem = validar_cep(cep)
    if not cep_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    cargo = Prompt.ask("[yellow]Cargo[/yellow]")

    email = Prompt.ask("[yellow]E-mail[/yellow]")
    email_valido, mensagem = validar_email(email)
    if not email_valido:
        console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        return

    senha = Prompt.ask("[yellow]Senha[/yellow]", password=True)
    cnpj_orgao = Prompt.ask("[yellow]CNPJ do Orgao Publico[/yellow] (14 digitos)")

    try:
        show_loading("Salvando dados")
        with conn.cursor() as cur:
            cur.execute("INSERT INTO USUARIO (CPF, TIPO) VALUES (%s, 'G')", (cpf,))
            numero_int = int(numero) if numero != "" else None
            cur.execute(
                """INSERT INTO USUARIO_GESTOR
                   (CPF, RUA, BAIRRO, NUMERO, CEP, CARGO, EMAIL, SENHA, CNPJ_ORGAO_PUBLICO)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (cpf, rua, bairro, numero_int, cep, cargo, email, senha, cnpj_orgao)
            )
        conn.commit()
        console.print("\n[green]Gestor cadastrado com sucesso![/green]")
    except psycopg2.IntegrityError as e:
        conn.rollback()
        console.print(f"\n[red]Erro de integridade:[/red] {e}")
    except Exception as e:
        conn.rollback()
        console.print(f"\n[red]Erro ao cadastrar:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

# CONSULTAS CIDADAO
def listar_viagens_por_cpf(conn, cpf=None):
    clear_screen()
    show_banner()

    if cpf is None:
        cpf = Prompt.ask("[cyan]CPF[/cyan] (11 digitos)")

        cpf_valido, mensagem = validar_cpf(cpf)
        if not cpf_valido:
            console.print(f"\n[red]Erro de validacao:[/red] {mensagem}")
            console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            return

    show_loading("Buscando viagens")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT v.DATAHORA_INICIO, v.DATAHORA_FINAL, v.CUSTO_TOTAL,
                          v.NOME_CODIGO_LINHA_EMBARQUE, v.NRO_PARADA_EMBARQUE,
                          v.NOME_CODIGO_LINHA_DESEMBARQUE, v.NRO_PARADA_DESEMBARQUE,
                          o.PLACA, l.TARIFA
                   FROM VIAGEM v
                   JOIN ONIBUS o ON v.PLACA_ONIBUS = o.PLACA
                   JOIN LINHA l ON v.NOME_CODIGO_LINHA_EMBARQUE = l.NOME_CODIGO
                   WHERE v.CPF_CIDADAO = %s
                   ORDER BY v.DATAHORA_INICIO DESC;""",
                (cpf,)
            )
            rows = cur.fetchall()

            if not rows:
                console.print(f"\n[yellow]Nenhuma viagem encontrada para o CPF {cpf}[/yellow]")
            else:
                table = Table(title=f"Viagens do CPF {cpf}",
                            title_style="bold cyan",
                            box=box.ROUNDED,
                            border_style="cyan")

                table.add_column("Data/Hora Inicio", style="cyan")
                table.add_column("Data/Hora Fim", style="cyan")
                table.add_column("Embarque", style="green")
                table.add_column("Desembarque", style="red")
                table.add_column("Placa", style="yellow")
                table.add_column("Custo", style="bold green", justify="right")

                for row in rows:
                    data_inicio, data_fim, custo, linha_emb, parada_emb, linha_des, parada_des, placa, tarifa = row
                    table.add_row(
                        str(data_inicio),
                        str(data_fim),
                        f"{linha_emb} (P{parada_emb})",
                        f"{linha_des} (P{parada_des})",
                        placa,
                        f"R$ {float(custo):.2f}"
                    )

                console.print("\n")
                console.print(table)
    except Exception as e:
        console.print(f"\n[red]Erro ao consultar viagens:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def total_gasto_por_cidadao(conn, cpf):
    clear_screen()
    show_banner()

    show_loading("Calculando total gasto")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(SUM(CUSTO_TOTAL), 0), COUNT(*)
                   FROM VIAGEM WHERE CPF_CIDADAO = %s""",
                (cpf,)
            )
            total, quantidade = cur.fetchone()

            panel = Panel(
                f"[bold green]R$ {float(total):.2f}[/bold green]\n\n"
                f"[dim]Total de viagens: {quantidade}[/dim]",
                title=f"Total Gasto - CPF {cpf}",
                border_style="green",
                box=box.DOUBLE
            )
            console.print("\n")
            console.print(panel, justify="center")
    except Exception as e:
        console.print(f"\n[red]Erro ao calcular total:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def consultar_linhas_disponiveis(conn):
    clear_screen()
    show_banner()

    bairro = Prompt.ask("[cyan]Informe o bairro[/cyan]")

    show_loading("Buscando linhas")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT DISTINCT l.NOME_CODIGO, l.TARIFA, l.TEMPO_PERCURSO, e.NOME
                   FROM LINHA l
                   JOIN PONTO_PARADA p ON p.NOME_CODIGO_LINHA = l.NOME_CODIGO
                   JOIN EMPRESA_PUBLICA e ON l.CNPJ_EMPRESA_PUBLICA = e.CNPJ
                   WHERE p.BAIRRO ILIKE %s AND l.ATIVO = 'S'
                   ORDER BY l.NOME_CODIGO;""",
                (bairro,)
            )
            rows = cur.fetchall()

            if not rows:
                console.print(f"\n[yellow]Nenhuma linha encontrada para o bairro '{bairro}'[/yellow]")
            else:
                table = Table(title=f"Linhas Disponiveis - {bairro}",
                            title_style="bold cyan",
                            box=box.ROUNDED,
                            border_style="cyan")

                table.add_column("Linha", style="bold cyan")
                table.add_column("Tarifa", style="green", justify="right")
                table.add_column("Tempo", style="yellow", justify="center")
                table.add_column("Empresa", style="blue")

                for nome_codigo, tarifa, tempo, empresa in rows:
                    table.add_row(
                        nome_codigo,
                        f"R$ {float(tarifa):.2f}",
                        f"{tempo} min" if tempo else "N/A",
                        empresa
                    )

                console.print("\n")
                console.print(table)
    except Exception as e:
        console.print(f"\n[red]Erro ao consultar linhas:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def consultar_pontos_parada(conn):
    clear_screen()
    show_banner()

    bairro = Prompt.ask("[cyan]Informe o bairro[/cyan]")
    rua = Prompt.ask("[cyan]Informe a rua[/cyan]")

    show_loading("Buscando pontos de parada")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT NOME_CODIGO_LINHA, NRO_PARADA, RUA, BAIRRO, NUMERO, CEP,
                          PRESENCA_COBERTURA, EH_ORIGEM, EH_DESTINO
                   FROM PONTO_PARADA
                   WHERE BAIRRO ILIKE %s AND RUA ILIKE %s
                   ORDER BY NOME_CODIGO_LINHA, NRO_PARADA;""",
                (bairro, rua)
            )
            rows = cur.fetchall()

            if not rows:
                console.print(f"\n[yellow]Nenhum ponto encontrado em {rua} - {bairro}[/yellow]")
            else:
                table = Table(title=f"Pontos de Parada - {rua}, {bairro}",
                            title_style="bold cyan",
                            box=box.ROUNDED,
                            border_style="cyan")

                table.add_column("Linha", style="cyan")
                table.add_column("Parada", style="yellow", justify="center")
                table.add_column("Endereco", style="white")
                table.add_column("Cobertura", style="green", justify="center")
                table.add_column("Origem", justify="center")
                table.add_column("Destino", justify="center")

                for linha, nro, rua_p, bairro_p, num, cep, cob, orig, dest in rows:
                    table.add_row(
                        linha,
                        str(nro),
                        f"{rua_p}, {num} - {bairro_p}",
                        "SIM" if cob == 'S' else "NAO",
                        "SIM" if orig == 'S' else "NAO",
                        "SIM" if dest == 'S' else "NAO"
                    )

                console.print("\n")
                console.print(table)
    except Exception as e:
        console.print(f"\n[red]Erro ao consultar pontos:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

# CONSULTAS GESTOR
def listar_linhas_ativas(conn):
    clear_screen()
    show_banner()

    show_loading("Carregando linhas ativas")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT l.NOME_CODIGO, l.TARIFA, l.TEMPO_PERCURSO, e.NOME
                   FROM LINHA l
                   JOIN EMPRESA_PUBLICA e ON l.CNPJ_EMPRESA_PUBLICA = e.CNPJ
                   WHERE l.ATIVO = 'S'
                   ORDER BY l.NOME_CODIGO;"""
            )
            rows = cur.fetchall()

            if not rows:
                console.print("\n[yellow]Nenhuma linha ativa encontrada[/yellow]")
            else:
                table = Table(title="Linhas Ativas",
                            title_style="bold yellow",
                            box=box.DOUBLE,
                            border_style="yellow")

                table.add_column("Linha", style="bold yellow")
                table.add_column("Tarifa", style="green", justify="right")
                table.add_column("Tempo Percurso", style="cyan", justify="center")
                table.add_column("Empresa", style="blue")

                for nome, tarifa, tempo, empresa in rows:
                    table.add_row(
                        nome,
                        f"R$ {float(tarifa):.2f}",
                        f"{tempo} min" if tempo else "N/A",
                        empresa
                    )

                console.print("\n")
                console.print(table)
    except Exception as e:
        console.print(f"\n[red]Erro ao listar linhas:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def viagens_por_linha(conn):
    clear_screen()
    show_banner()

    show_loading("Analisando viagens por linha")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT v.NOME_CODIGO_LINHA_EMBARQUE, COUNT(*) as qtd
                   FROM VIAGEM v
                   GROUP BY v.NOME_CODIGO_LINHA_EMBARQUE
                   ORDER BY qtd DESC;"""
            )
            rows = cur.fetchall()

            if not rows:
                console.print("\n[yellow]Nenhuma viagem registrada[/yellow]")
            else:
                table = Table(title="Viagens por Linha",
                            title_style="bold yellow",
                            box=box.ROUNDED,
                            border_style="yellow")

                table.add_column("Linha", style="cyan", justify="left")
                table.add_column("Quantidade", style="bold green", justify="right")
                table.add_column("Grafico", style="blue")

                max_qtd = max(qtd for _, qtd in rows)

                for linha, qtd in rows:
                    bar_length = int((qtd / max_qtd) * 30)
                    bar = "#" * bar_length
                    table.add_row(linha, str(qtd), bar)

                console.print("\n")
                console.print(table)
    except Exception as e:
        console.print(f"\n[red]Erro ao listar viagens:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def rotas_mais_utilizadas(conn):
    clear_screen()
    show_banner()

    show_loading("Analisando rotas mais utilizadas")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT pe.BAIRRO, pd.BAIRRO, COUNT(*) as qtd
                   FROM VIAGEM v
                   JOIN PONTO_PARADA pe ON v.NOME_CODIGO_LINHA_EMBARQUE = pe.NOME_CODIGO_LINHA
                       AND v.NRO_PARADA_EMBARQUE = pe.NRO_PARADA
                   JOIN PONTO_PARADA pd ON v.NOME_CODIGO_LINHA_DESEMBARQUE = pd.NOME_CODIGO_LINHA
                       AND v.NRO_PARADA_DESEMBARQUE = pd.NRO_PARADA
                   WHERE pe.BAIRRO IS NOT NULL AND pd.BAIRRO IS NOT NULL
                   GROUP BY pe.BAIRRO, pd.BAIRRO
                   ORDER BY qtd DESC
                   LIMIT 10;"""
            )
            rows = cur.fetchall()

            if not rows:
                console.print("\n[yellow]Nenhuma rota registrada[/yellow]")
            else:
                table = Table(title="Top 10 Rotas Mais Utilizadas",
                            title_style="bold yellow",
                            box=box.DOUBLE,
                            border_style="yellow")

                table.add_column("#", style="dim", justify="center", width=4)
                table.add_column("Origem", style="green")
                table.add_column("->", style="yellow", justify="center", width=3)
                table.add_column("Destino", style="red")
                table.add_column("Viagens", style="bold cyan", justify="right")

                for i, (origem, destino, qtd) in enumerate(rows, 1):
                    table.add_row(str(i), origem, "->", destino, str(qtd))

                console.print("\n")
                console.print(table)
    except Exception as e:
        console.print(f"\n[red]Erro ao listar rotas:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def horarios_de_pico(conn):
    clear_screen()
    show_banner()

    show_loading("Analisando horarios de pico")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT EXTRACT(HOUR FROM DATAHORA_INICIO) as hora, COUNT(*) as qtd
                   FROM VIAGEM
                   GROUP BY hora
                   ORDER BY qtd DESC;"""
            )
            rows = cur.fetchall()

            if not rows:
                console.print("\n[yellow]Nenhuma viagem registrada[/yellow]")
            else:
                table = Table(title="Horarios de Pico",
                            title_style="bold yellow",
                            box=box.ROUNDED,
                            border_style="yellow")

                table.add_column("Horario", style="cyan", justify="center")
                table.add_column("Viagens", style="bold green", justify="right")
                table.add_column("Grafico", style="blue")

                max_qtd = max(qtd for _, qtd in rows)
                sorted_rows = sorted(rows, key=lambda x: x[0])

                for hora, qtd in sorted_rows:
                    bar_length = int((qtd / max_qtd) * 30)
                    bar = "#" * bar_length
                    table.add_row(f"{int(hora):02d}:00", str(qtd), bar)

                console.print("\n")
                console.print(table)
    except Exception as e:
        console.print(f"\n[red]Erro ao listar horarios:[/red] {e}")

    console.input("\n[dim]Pressione Enter para continuar...[/dim]")

# LOGIN
def entrar_como_cidadao(conn):
    clear_screen()
    show_banner()

    console.print(Panel.fit(
        "[bold cyan]Login de Cidadao[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    email = Prompt.ask("[cyan]Email[/cyan]")
    senha = Prompt.ask("[cyan]Senha[/cyan]", password=True)

    show_loading("Autenticando")

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT CPF FROM USUARIO_CIDADAO WHERE EMAIL = %s AND SENHA = %s",
                (email, senha)
            )
            result = cur.fetchone()

        if not result:
            console.print("\n[red]Email ou senha invalidos![/red]")
            console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            return

        cpf = result[0]
        console.print(f"\n[green]Login bem-sucedido![/green] [dim](CPF: {cpf})[/dim]")
        time.sleep(1)
        menu_cidadao(conn, cpf)
    except Exception as e:
        console.print(f"\n[red]Erro ao fazer login:[/red] {e}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def entrar_como_gestor(conn):
    clear_screen()
    show_banner()

    console.print(Panel.fit(
        "[bold yellow]Login de Gestor[/bold yellow]",
        border_style="yellow"
    ))
    console.print()

    email = Prompt.ask("[yellow]Email[/yellow]")
    senha = Prompt.ask("[yellow]Senha[/yellow]", password=True)

    show_loading("Autenticando")

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM USUARIO_GESTOR WHERE EMAIL = %s AND SENHA = %s",
                (email, senha)
            )
            result = cur.fetchone()

        if not result:
            console.print("\n[red]Email ou senha invalidos![/red]")
            console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            return

        console.print(f"\n[green]Login bem-sucedido![/green] [dim](Email: {email})[/dim]")
        time.sleep(1)
        menu_gestor(conn, email)
    except Exception as e:
        console.print(f"\n[red]Erro ao fazer login:[/red] {e}")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")

# MENUS
def menu_cidadao(conn, cpf):
    while True:
        opcoes = [
            "Listar minhas viagens",
            "Ver total gasto",
            "Consultar linhas por bairro",
            "Consultar pontos de parada",
            "Voltar ao menu principal"
        ]

        escolha = menu_select(
            "Menu do Cidadao",
            opcoes,
            f"[cyan]Logado como:[/cyan] CPF {cpf}"
        )

        if escolha == 0:
            listar_viagens_por_cpf(conn, cpf)
        elif escolha == 1:
            total_gasto_por_cidadao(conn, cpf)
        elif escolha == 2:
            consultar_linhas_disponiveis(conn)
        elif escolha == 3:
            consultar_pontos_parada(conn)
        elif escolha == 4:
            break

def menu_gestor(conn, email):
    while True:
        opcoes = [
            "Listar linhas ativas",
            "Viagens por linha",
            "Rotas mais utilizadas",
            "Horarios de pico",
            "Voltar ao menu principal"
        ]

        escolha = menu_select(
            "Menu do Gestor",
            opcoes,
            f"[yellow]Logado como:[/yellow] {email}"
        )

        if escolha == 0:
            listar_linhas_ativas(conn)
        elif escolha == 1:
            viagens_por_linha(conn)
        elif escolha == 2:
            rotas_mais_utilizadas(conn)
        elif escolha == 3:
            horarios_de_pico(conn)
        elif escolha == 4:
            break

# MENU PRINCIPAL
def main():
    show_banner()
    time.sleep(1)

    conn = get_connection()
    if not conn:
        console.print("[red]Nao foi possivel conectar ao banco. Encerrando.[/red]")
        return

    while True:
        opcoes = [
            "Cadastrar novo cidadao",
            "Cadastrar novo gestor",
            "Entrar como cidadao",
            "Entrar como gestor",
            "Informacoes para DEBUG",
            "Sair"
        ]

        escolha = menu_select(
            "MENU PRINCIPAL",
            opcoes,
            "Sistema de Gerenciamento de Transporte Publico"
        )

        if escolha == 0:
            cadastrar_cidadao(conn)
        elif escolha == 1:
            cadastrar_gestor(conn)
        elif escolha == 2:
            entrar_como_cidadao(conn)
        elif escolha == 3:
            entrar_como_gestor(conn)
        elif escolha == 4:
            mostrar_info_debug(conn)
        elif escolha == 5:
            clear_screen()
            show_banner()
            console.print("[yellow]Encerrando sistema...[/yellow]", justify="center")
            time.sleep(0.5)
            console.print("[green]Ate logo![/green]", justify="center")
            break

    conn.close()

if __name__ == "__main__":
    main()
