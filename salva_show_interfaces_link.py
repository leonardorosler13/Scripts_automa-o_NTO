from netmiko import ConnectHandler
from getpass import getpass
from pathlib import Path
from datetime import datetime

# =====================================================
# PASTAS
# =====================================================

PASTA_BASE = Path(__file__).resolve().parent

ARQUIVO_IPS = PASTA_BASE / "lista_ip_switches.txt"

PASTA_SHOW_INTERFACES = PASTA_BASE / "show_interfaces"

PASTA_SHOW_INTERFACES.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# CREDENCIAIS
# =====================================================

username = input("Usuário: ")
password = getpass("Senha: ")

# =====================================================
# VALIDAÇÃO DO ARQUIVO DE IPS
# =====================================================

if not ARQUIVO_IPS.exists():
    print(f"Arquivo não encontrado: {ARQUIVO_IPS}")
    exit()

# =====================================================
# LEITURA DOS IPS
# =====================================================

with open(ARQUIVO_IPS, "r", encoding="utf-8") as f:
    switches = [linha.strip() for linha in f if linha.strip()]

if not switches:
    print("Nenhum IP encontrado em lista_ip_switches.txt")
    exit()

# =====================================================
# PROCESSAMENTO DOS SWITCHES
# =====================================================

switches_processados = 0
switches_falharam = []

for ip in switches:

    print(f"\nConectando em {ip}...")

    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
    }

    try:

        connection = ConnectHandler(**device)

        #nome_relatorio = PASTA_SHOW_INTERFACES / f"{ip}.txt"
        data_hora = datetime.now().strftime("%y%m%d_%H%M%S")
        nome_relatorio = PASTA_SHOW_INTERFACES / f"{ip}_{data_hora}.txt"

        connection.send_command_timing("terminal length 0")

        print("Executando: show interfaces link")

        output = connection.send_command(
            "show interfaces link",
            read_timeout=120
        )   
        
        hostname = connection.find_prompt().rstrip("#")
        
        with open(nome_relatorio, "w", encoding="utf-8") as arquivo:
            arquivo.write(f"SWITCH: {hostname}\n")
            arquivo.write(f"IP: {ip}\n")
            arquivo.write("=" * 80 + "\n")
            arquivo.write(output)
            
        switches_processados += 1    

        connection.send_command_timing("terminal length 24")

        connection.disconnect()

        print(f"{ip}: OK")
        print(f"Linhas capturadas: {len(output.splitlines())}")
        print(f"Relatório salvo em: {nome_relatorio}")

    except Exception as e:

        switches_falharam.append(ip)
        
        print(f"{ip}: ERRO - {e}")

# =====================================================
# FIM
# =====================================================

if switches_processados == 0:

    print("\nERRO: Nenhum switch foi acessado com sucesso.")
    print("Verifique usuário, senha ou conectividade.")

    raise SystemExit(1)

print("\n" + "=" * 80)
print("RESUMO DA COLETA")
print("=" * 80)

print(
    f"Sucesso : {switches_processados}/{len(switches)}"
)

print(
    f"Falhas  : {len(switches_falharam)}"
)

if switches_falharam:

    print("\nSwitches inacessíveis:")

    for ip in switches_falharam:
        print(f" - {ip}")

print("=" * 80)
print("\nProcessamento concluído.")