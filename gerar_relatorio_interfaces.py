import re
from pathlib import Path
from datetime import datetime

# =====================================================
# CONFIGURAÇÕES
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

PASTA_LOGS = BASE_DIR / "show_interfaces"
PASTA_RELATORIO = BASE_DIR / "relatorio_int_down_x_dias"

# =====================================================
# DIAS
# =====================================================

while True:

    try:

        LIMITE_DIAS = int(
            input("Digite a quantidade de dias: ")
        )

        if LIMITE_DIAS < 0:

            print(
                "Digite um valor maior ou igual a zero."
            )

            continue

        break

    except ValueError:

        print(
            "Valor inválido. Digite apenas números."
        )

# =====================================================
# DEBUG
# =====================================================

DEBUG = True

if DEBUG:

    print("\n" + "=" * 80)
    print("MODO DEPURAÇÃO")
    print("=" * 80)
    print(f"Script.............: {Path(__file__).name}")
    print(f"Pasta do script....: {BASE_DIR}")
    print(f"Pasta de logs......: {PASTA_LOGS}")
    print(f"Pasta de relatório.: {PASTA_RELATORIO}")
    print("=" * 80 + "\n")

# =====================================================
# VALIDAÇÕES
# =====================================================

if not PASTA_LOGS.exists():

    print(
        "\nERRO: Pasta de logs não encontrada."
    )

    print(
        f"Caminho esperado: {PASTA_LOGS}"
    )

    raise SystemExit(1)

PASTA_RELATORIO.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# CONVERSÃO DE TEMPO
# =====================================================

def converte_tempo_para_dias(texto):

    texto = texto.lower().strip()

    dias = 0

    semanas = re.search(
        r"(\d+)w",
        texto
    )

    if semanas:
        dias += int(semanas.group(1)) * 7

    dias_match = re.search(
        r"(\d+)d",
        texto
    )

    if dias_match:
        dias += int(dias_match.group(1))

    return dias

# =====================================================
# HOSTNAME
# =====================================================

def obter_hostname(conteudo, arquivo):

    for linha in conteudo.splitlines():
        match = re.match(
            r"^SWITCH:\s*(.+)$",
            linha.strip()
        )
        if match:
            return match.group(1)

    for linha in conteudo.splitlines():
        match = re.search(
            r"^(\S+)#show interfaces link",
            linha
        )
        if match:
            return match.group(1)

    nome = Path(arquivo).stem

    match = re.match(
        r"^(\d+\.\d+\.\d+\.\d+)",
        nome
    )

    if match:
        return match.group(1)

    return nome
# =====================================================
# HOSTNAME E IP
# =====================================================
def obter_dados_switch(conteudo, arquivo):

    hostname = None
    ip = None

    for linha in conteudo.splitlines():

        match = re.match(
            r"^SWITCH:\s*(.+)$",
            linha.strip()
        )
        if match:
            hostname = match.group(1)

        match = re.match(
            r"^IP:\s*(.+)$",
            linha.strip()
        )
        if match:
            ip = match.group(1)
    if not hostname:
        hostname = Path(arquivo).stem        

    return hostname, ip

# =====================================================
# PROCESSAMENTO
# =====================================================

def processar_arquivo(arquivo):

    resultado = []

    try:

        with open(
            arquivo,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            conteudo = f.read()

    except Exception as erro:

        print(
            f"Erro ao abrir {arquivo}: {erro}"
        )

        return resultado

#    hostname = obter_hostname(
#        conteudo,
#        arquivo
#    )
    hostname, ip = obter_dados_switch(
        conteudo,
        arquivo
    )

    dentro_tabela = False

    for linha in conteudo.splitlines():

        linha_original = linha
        linha = linha.rstrip()

        # Cabeçalho da tabela

        if (
            "Port" in linha
            and
            "Down Time" in linha
        ):

            dentro_tabela = True
            continue

        if not dentro_tabela:
            continue

        if not linha.strip():
            continue

        if "#" in linha:
            break

        partes = linha.split()

        if len(partes) < 2:
            continue

        porta = partes[0]

        # Apenas interfaces Gigabit

        if not porta.startswith("Gi"):
            continue

        #
        # EXEMPLOS:
        #
        # DOWN:
        # Gi1/0/8                     3w2d
        #
        # DOWN COM NOME:
        # Gi1/0/15 AP-NTO-TI          3w2d
        #
        # UP:
        # Gi1/0/18                   00:00:00 2w6d
        #
        # UP COM NOME:
        # Gi1/0/15 AP-NTO-TI         00:00:00 3w2d
        #

        # Se existe 00:00:00 na linha,
        # a interface está UP

        if "00:00:00" in linha_original:
            continue

        down_time = partes[-1]

        descricao = ""

        if len(partes) > 2:

            descricao = " ".join(
                partes[1:-1]
            )

        dias = converte_tempo_para_dias(
            down_time
        )

        if dias >= LIMITE_DIAS:

            resultado.append(
                {
                    "switch": hostname,
                    "ip": ip,
                    "interface": porta,
                    "descricao": descricao,
                    "down_time": down_time,
                    "dias": dias,
                    "arquivo": Path(arquivo).name
                }
            )

    return resultado

# =====================================================
# ORDENAÇÃO
# =====================================================

def chave_interface(item):

    match = re.match(
        r"Gi(\d+)/(\d+)/(\d+)",
        item["interface"]
    )

    if match:

        return (
            item["switch"],
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3))
        )

    return (
        item["switch"],
        999,
        999,
        999
    )

# =====================================================
# RELATÓRIO
# =====================================================

def gerar_relatorio(resultado):

    if not resultado:

        print(
            f"Nenhuma interface DOWN com mais de {LIMITE_DIAS} dias encontrada."
        )

        return

    resultado.sort(
        key=chave_interface
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    arquivo_saida = (
        PASTA_RELATORIO /
        f"interfaces_down_mais_{LIMITE_DIAS}_dias_{timestamp}.txt"
    )

    with open(
        arquivo_saida,
        "w",
        encoding="utf-8"
    ) as relatorio:

        relatorio.write(
            "=" * 120 + "\n"
        )

        relatorio.write(
            f"RELATORIO DE INTERFACES DOWN MAIOR QUE {LIMITE_DIAS} DIAS\n"
        )

        relatorio.write(
            f"GERADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        )

        relatorio.write(
            "=" * 120 + "\n"
        )

        switch_atual = ""

        total_switch = 0

        for item in resultado:

#            if item["switch"] != switch_atual:
#
#                switch_atual = item["switch"]
#
#                total_switch += 1
#
#                relatorio.write("\n")
#
#                relatorio.write(
#                    f"SWITCH: {switch_atual}\n"
#                )
#
#                relatorio.write(
#                    "-" * 120 + "\n"
#                )
            if item["switch"] != switch_atual:
            
                switch_atual = item["switch"]
            
                total_switch += 1
            
                relatorio.write("\n")

                relatorio.write(
                    f"SWITCH: {switch_atual}\n"
                )
            
                relatorio.write(
                    f"IP: {item['ip']}\n"
                )
            
                relatorio.write(
                    "-" * 120 + "\n"
                )

                relatorio.write(
                    f"{'INTERFACE':<15}"
                    f"{'DESCRICAO':<40}"
                    f"{'DOWN TIME':<20}"
                    f"{'DIAS'}\n"
                )

                relatorio.write(
                    "-" * 120 + "\n"
                )

            relatorio.write(
                f"{item['interface']:<15}"
                f"{item['descricao']:<40}"
                f"{item['down_time']:<20}"
                f"{item['dias']}\n"
            )

        relatorio.write("\n")

        relatorio.write(
            "=" * 120 + "\n"
        )

        relatorio.write(
            f"TOTAL DE SWITCHES: {total_switch}\n"
        )

        relatorio.write(
            f"TOTAL DE INTERFACES DOWN: {len(resultado)}\n"
        )

        relatorio.write(
            "=" * 120 + "\n"
        )

    print()
    print("=" * 80)
    print("RELATÓRIO GERADO COM SUCESSO")
    print("=" * 80)
    print(f"Arquivo: {arquivo_saida}")
    print(
        f"Total de interfaces encontradas: {len(resultado)}"
    )
    print("=" * 80)

# =====================================================
# MAIN
# =====================================================

def main():

    arquivos = (
        list(
            PASTA_LOGS.rglob("*.txt")
        )
        +
        list(
            PASTA_LOGS.rglob("*.log")
        )
    )

    if not arquivos:

        print(
            f"Nenhum arquivo encontrado em:\n{PASTA_LOGS}"
        )

        return

    print()
    print(
        f"Arquivos encontrados: {len(arquivos)}"
    )

    for arquivo in arquivos:

        print(
            f"  - {arquivo.name}"
        )

    print()

    resultado_total = []

    for arquivo in arquivos:

        print(
            f"Processando: {arquivo.name}"
        )

        resultado_switch = processar_arquivo(
            arquivo
        )

        print(
            f"Interfaces DOWN encontradas: {len(resultado_switch)}"
        )

        resultado_total.extend(
            resultado_switch
        )

    gerar_relatorio(
        resultado_total
    )

# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == "__main__":
    main()