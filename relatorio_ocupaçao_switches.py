from netmiko import ConnectHandler
import pandas as pd
import re
from getpass import getpass
from pathlib import Path

#ARQUIVO_IPS = "lista_ip_switches.txt"
BASE_DIR = Path(__file__).parent
ARQUIVO_IPS = BASE_DIR / "lista_ip_switches.txt"

usuario = input("Usuário: ")
senha = getpass("Senha: ")

resultado = []

with open(ARQUIVO_IPS, "r") as f:
    ips = [linha.strip() for linha in f if linha.strip()]

for ip in ips:

    print(f"\nConectando em {ip}...")

    try:

        conexao = ConnectHandler(
            device_type="cisco_ios",
            host=ip,
            username=usuario,
            password=senha,
            fast_cli=False
        )

        hostname_output = conexao.send_command(
            "show running-config | include ^hostname"
        )

        hostname = hostname_output.replace(
            "hostname",
            ""
        ).strip()

        print(f"Coletando informações de {hostname}...")

        # Obtém configuração das interfaces
        running_config = conexao.send_command(
            "show running-config | section ^interface",
            read_timeout=120
        )

        # Obtém informações do stack
        stack_output = conexao.send_command(
            "show switch",
            read_timeout=60
        )

        # Captura blocos completos de interfaces
        interfaces = re.findall(
            r"^interface GigabitEthernet.*?(?=^interface|\Z)",
            running_config,
            flags=re.S | re.M
        )

        # Remove interface de gerenciamento
        interfaces = [
            interface
            for interface in interfaces
            if not interface.startswith(
                "interface GigabitEthernet0/0"
            )
        ]

        total = len(interfaces)

        disponiveis = sum(
            1
            for interface in interfaces
            if re.search(
                r"^\s*description\s+DISPONIVEL\s*$",
                interface,
                flags=re.I | re.M
            )
        )

        utilizadas = total - disponiveis

        percentual = round(
            (utilizadas / total) * 100,
            2
        ) if total > 0 else 0

        # Descobrir quantidade de membros no stack

        membros_stack = set()

        for linha in stack_output.splitlines():

            match = re.match(
                r"^\*?\s*(\d+)\s+",
                linha
            )

            if match:
                membros_stack.add(match.group(1))

        qtd_caixas = len(membros_stack)

        # Caso não seja stack
        if qtd_caixas == 0:
            qtd_caixas = 1

        resultado.append({
            "Hostname": hostname,
            "IP": ip,
            "Caixas Stack": qtd_caixas,
            "Total Portas": total,
            "Utilizadas": utilizadas,
            "Disponiveis": disponiveis,
            "% Ocupacao": percentual
        })

        print(
            f"OK - Portas: {total} | "
            f"Utilizadas: {utilizadas} | "
            f"Disponíveis: {disponiveis} | "
            f"Stack: {qtd_caixas}"
        )

        conexao.disconnect()

    except Exception as erro:

        print(f"Falha em {ip}: {erro}")

        resultado.append({
            "Hostname": "ERRO",
            "IP": ip,
            "Caixas Stack": 0,
            "Total Portas": 0,
            "Utilizadas": 0,
            "Disponiveis": 0,
            "% Ocupacao": 0
        })

df = pd.DataFrame(resultado)
from datetime import datetime
data_hora = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
arquivo_saida = f"relatorio_ocupacao_switches_{data_hora}.xlsx"

#arquivo_saida = "relatorio_ocupacao_switches.xlsx"

df.to_excel(
    arquivo_saida,
    index=False
)

print("\nRelatório gerado com sucesso:")
print(arquivo_saida)

print("\nResumo:")
print(df)