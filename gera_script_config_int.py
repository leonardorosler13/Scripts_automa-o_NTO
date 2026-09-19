import re
from pathlib import Path
from datetime import datetime

# =====================================================
# PASTAS
# =====================================================

PASTA_BASE = Path(__file__).resolve().parent

PASTA_RELATORIOS = (
    PASTA_BASE / "relatorio_int_down_x_dias"
)

PASTA_SAIDA = (
    PASTA_BASE / "script_config_int"
)

PASTA_SAIDA.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# VALIDAÇÃO
# =====================================================

if not PASTA_RELATORIOS.exists():

    print(
        f"Pasta não encontrada:\n{PASTA_RELATORIOS}"
    )

    raise SystemExit(1)

# =====================================================
# PEGA O RELATÓRIO MAIS RECENTE
# =====================================================

arquivos = sorted(
    PASTA_RELATORIOS.glob("*.txt"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

if not arquivos:

    print("Nenhum relatório encontrado.")

    raise SystemExit(1)

arquivo_relatorio = arquivos[0]

print()
print("=" * 80)
print("RELATÓRIO UTILIZADO")
print("=" * 80)
print(arquivo_relatorio.name)
print("=" * 80)
print()

# =====================================================
# ARMAZENAMENTO
# =====================================================

switches = {}
ips_switches = {}

# =====================================================
# LEITURA DO RELATÓRIO
# =====================================================

with open(
    arquivo_relatorio,
    "r",
    encoding="utf-8",
    errors="ignore"
) as f:

    linhas = f.readlines()

switch_atual = None

#for linha in linhas:
#
#    linha = linha.strip()
#
#    if not linha:
#        continue

for linha in linhas:

    linha = linha.strip()

    if not linha:
        continue

    match_switch = re.match(
        r"^SWITCH:\s*(.+)$",
        linha
    )

    if match_switch:

        switch_atual = (
            match_switch.group(1)
            .strip()
        )

        if switch_atual not in switches:
            switches[switch_atual] = set()

        print(
            f"Switch encontrado: {switch_atual}"
        )

        continue

    if linha.startswith("IP:"):

        if switch_atual:

            ips_switches[switch_atual] = (
                linha.split(":", 1)[1]
                .strip()
            )

        continue

    # =================================================
    # SWITCH
    # =================================================

    match_switch = re.match(
        r"^SWITCH:\s*(.+)$",
        linha
    )

    if match_switch:

        switch_atual = (
            match_switch.group(1)
            .strip()
        )

        if switch_atual not in switches:

            switches[switch_atual] = set()
            match_ip = re.match(
                r"^IP:\s*(.+)$",
                linha
        )

        if match_ip and switch_atual:
            ips_switches[switch_atual] = match_ip.group(1)

        print(
            f"Switch encontrado: {switch_atual}"
        )

        continue

    # =================================================
    # IGNORA CABEÇALHOS
    # =================================================

    if (
        linha.startswith("INTERFACE")
        or linha.startswith("TOTAL")
        or linha.startswith("=")
        or linha.startswith("-")
        or linha.startswith("GERADO")
        or linha.startswith("RELATORIO")
    ):
        continue

    # =================================================
    # INTERFACE
    # =================================================

    match_int = re.search(
        r"(Gi\d+/\d+/\d+)",
        linha
    )

    if match_int and switch_atual:

        interface = match_int.group(1)

        interface = interface.replace(
            "Gi",
            "GigabitEthernet",
            1
        )

        switches[switch_atual].add(
            interface
        )

# =====================================================
# RESUMO
# =====================================================

print()
print("=" * 80)
print("RESUMO")
print("=" * 80)

for switch, interfaces in switches.items():

    print(
        f"{switch}: {len(interfaces)} interfaces"
    )

print("=" * 80)
print()

# =====================================================
# ORDENAÇÃO
# =====================================================

def ordenar_interface(interface):

    match = re.search(
        r"(\d+)/(\d+)/(\d+)",
        interface
    )

    if match:

        return (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3))
        )

    return (
        999,
        999,
        999
    )

# =====================================================
# GERA UM SCRIPT POR SWITCH
# =====================================================

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

for switch, interfaces in switches.items():

    if not interfaces:
        continue

    nome_arquivo = re.sub(
        r'[\\/:*?"<>| ]',
        "_",
        switch
    )

    arquivo_saida = (
        PASTA_SAIDA /
        f"{nome_arquivo}_{timestamp}.txt"
    )

    with open(
        arquivo_saida,
        "w",
        encoding="utf-8"
    ) as f:
    
        ip = ips_switches.get(
        switch,
        "IP_NAO_ENCONTRADO"
        )    
        
        f.write(f"! HOSTNAME: {switch}\n")
        f.write(f"! IP: {ip}\n")
        f.write("!\n")
#        f.write("configure terminal\n")
      
        for interface in sorted(
            interfaces,
            key=ordenar_interface
        ):

            f.write("\n!\n")
            f.write(
                f"default interface {interface}\n"
            )
            f.write(
                f"interface {interface}\n"
            )
            f.write(
                " description DISPONIVEL\n"
            )
            f.write(
                " storm-control broadcast level 1.00 0.50\n"
            )
            f.write(
                " storm-control multicast level 2.00 1.00\n"
            )
            f.write(
                " storm-control action shutdown\n"
            )
            f.write(
                " spanning-tree bpduguard enable\n"
            )
            f.write(
                " shutdown\n"
            )

#        f.write("\nend\n")
#        f.write("write memory\n")

    print(
        f"Script criado: {arquivo_saida}"
    )

print()
print(
    f"Total de switches processados: {len(switches)}"
)