from netmiko import ConnectHandler
from getpass import getpass
from pathlib import Path
import re

# =====================================================
# PASTAS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

PASTA_SCRIPTS = BASE_DIR / "script_config_int"

PASTA_EXECUTADOS = (
    PASTA_SCRIPTS / "executados"
)

PASTA_EXECUTADOS.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# VALIDAÇÃO
# =====================================================

if not PASTA_SCRIPTS.exists():

    print(
        f"Pasta não encontrada:\n{PASTA_SCRIPTS}"
    )

    raise SystemExit(1)

#arquivos = sorted(
#    PASTA_SCRIPTS.glob("*.txt")
#)
todos_arquivos = sorted(
    PASTA_SCRIPTS.glob("*.txt"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

arquivos = []

switches_processados = set()

for arquivo in todos_arquivos:

    try:

        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as f:

            cabecalho = "".join(
                [next(f, "") for _ in range(5)]
            )

        match_host = re.search(
            r"HOSTNAME:\s*(.+)",
            cabecalho
        )

        if not match_host:
            continue

        hostname = (
            match_host.group(1)
            .strip()
        )

        if hostname in switches_processados:
            continue

        switches_processados.add(
            hostname
        )

        arquivos.append(
            arquivo
        )

    except Exception:
        continue

if not arquivos:

    print(
        "Nenhum script encontrado."
    )

    raise SystemExit(1)
print()
print("=" * 80)
print("SCRIPTS SELECIONADOS")
print("=" * 80)

for arquivo in arquivos:
    print(arquivo.name)

print("=" * 80)
print()

# =====================================================
# CREDENCIAIS
# =====================================================

username = input("Usuário: ")
password = getpass("Senha: ")

# =====================================================
# PROCESSAMENTO
# =====================================================

for arquivo in arquivos:

    nome_arquivo = arquivo.name

    # Exemplo:
    # 172.19.100.16_20260805_154600.txt

#    match = re.match(
#        r"^(\d+\.\d+\.\d+\.\d+)_",
#        nome_arquivo
#    )
#
#    if not match:
#
#        print(
#            f"\nIGNORADO (sem IP no nome): "
#            f"{nome_arquivo}"
#        )
#
#        continue
#
#    ip = match.group(1)

    with open(
        arquivo,
        "r",
        encoding="utf-8"
    ) as f:
    
        cabecalho = "".join(
            [next(f, "") for _ in range(5)]
        )
    
    match_ip = re.search(
        r"IP:\s*(\d+\.\d+\.\d+\.\d+)",
        cabecalho
    )
    
    match_host = re.search(
        r"HOSTNAME:\s*(.+)",
        cabecalho
    )
    
    if not match_ip:
        print(
            f"\nIGNORADO (IP não encontrado): "
            f"{arquivo.name}"
        )
        continue
    
    ip = match_ip.group(1)
    
    hostname = (
        match_host.group(1)
        if match_host
        else "DESCONHECIDO"
    )

    print("\n" + "=" * 80)
    print(f"SWITCH : {hostname}")
    print(f"IP     : {ip}")
    print(f"SCRIPT : {nome_arquivo}")
    print("=" * 80)

    try:

        device = {
            "device_type": "cisco_ios",
            "host": ip,
            "username": username,
            "password": password,
            "fast_cli": False
        }

        print(
            f"Conectando em {ip}..."
        )

        conn = ConnectHandler(
            **device
        )

        prompt = conn.find_prompt()

        print(
            f"Conectado em: {prompt}"
        )

# =================================================
# LÊ O SCRIPT
# =================================================

        with open(
            arquivo,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            comandos = []

#            for linha in f:
#
#                linha = linha.strip()
#
#                if not linha:
#                    continue
#
#                if linha == "!":
#                    continue
#
#                comandos.append(linha)
            for linha in f:
            
                linha = linha.strip()
            
                if not linha:
                    continue
            
                if linha == "!":
                    continue
            
                if linha.startswith("! HOSTNAME:"):
                    continue
            
                if linha.startswith("! IP:"):
                    continue
            
                comandos.append(linha)
        
        print(
            f"Comandos carregados: "
            f"{len(comandos)}"
        )

# =================================================
# EXECUÇÃO
# =================================================

        print()
        print("=" * 80)
        print("APLICANDO CONFIGURAÇÃO")
        print("=" * 80)

        output = conn.send_config_set(
            comandos,
            read_timeout=300
        )

        print(
            "Configuração aplicada."
        )

        output_save = conn.save_config()

        print(
        "Configuração salva."
        )

# =================================================
# TESTE OU PRODUÇÃO
# =================================================
#
#        if MODO_TESTE:
#
#            print()
#            print("=" * 80)
#            print("MODO TESTE ATIVO")
#            print("NENHUMA CONFIGURAÇÃO SERÁ APLICADA")
#            print("=" * 80)
#
#            print()
#            print(
#                "COMANDOS QUE SERIAM EXECUTADOS:"
#            )
#            print()
#
#            for cmd in comandos:
#                print(cmd)
#
#            output = (
#                "MODO TESTE - "
#                "NENHUM COMANDO EXECUTADO"
#            )
#
#            output_save = (
#                "MODO TESTE - "
#                "CONFIGURAÇÃO NÃO SALVA"
#            )
#
#            print()
#            print("=" * 80)
#            print("FIM DA SIMULAÇÃO")
#            print("=" * 80)
#
#        else:
#
#            print()
#            print("=" * 80)
#            print("MODO PRODUÇÃO")
#            print("=" * 80)
#
#            output = conn.send_config_set(
#                comandos,
#                read_timeout=300
#            )
#
#            print(
#                "Configuração aplicada."
#            )
#
#            output_save = conn.save_config()
#
#            print(
#                "Configuração salva."
#            )

# =================================================
# LOG
# =================================================

#        arquivo_log = (
#            arquivo.parent /
#            f"{arquivo.stem}_EXECUTADO.log"
#        )
        arquivo_log = (
            PASTA_EXECUTADOS /
            f"{arquivo.stem}_EXECUTADO.log"
        )

        with open(
            arquivo_log,
            "w",
            encoding="utf-8"
        ) as log:

            log.write(
                f"Switch: {ip}\n"
            )

            log.write(
                f"Prompt: {prompt}\n\n"
            )

            log.write(
                "===== CONFIG =====\n"
            )

            log.write(
                str(output)
            )

            log.write(
                "\n\n===== SAVE =====\n"
            )

            log.write(
                str(output_save)
            )

        print(
            f"Log salvo: "
            f"{arquivo_log.name}"
        )

#        conn.disconnect()
#
#        print(
#            f"{ip}: OK"
#        )
        conn.disconnect()

        arquivo.rename(
            PASTA_EXECUTADOS / arquivo.name
        )

        print(
            f"Script movido para executados: "
            f"{arquivo.name}"
        )
        print(
            f"{ip}: OK"
        )
    except Exception as erro:

        print(
            f"{ip}: ERRO -> {erro}"
        )

print()
print("=" * 80)
print("PROCESSAMENTO CONCLUÍDO")
print("=" * 80)