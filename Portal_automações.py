import sys
import subprocess
import pathlib

# =====================================================
# PASTA DOS SCRIPTS
# =====================================================
PASTA_SCRIPTS = pathlib.Path(r"C:\Automações")

# =====================================================
# VALIDAÇÃO DE ARQUIVOS OBRIGATÓRIOS
# =====================================================
ARQUIVOS_OBRIGATORIOS = [
    "salva_show_interfaces_link.py",
    "gerar_relatorio_interfaces.py",
    "gera_script_config_int.py",
    "aplica_config.py",
    "gerenciar_lista_ip_switches.py",
    "relatorio_ocupaçao_switches.py",
    "lista_ip_switches.txt"
]

# =====================================================
# EXECUTA SCRIPT
# =====================================================
def executar_script(nome_arquivo):

    arquivo = PASTA_SCRIPTS / nome_arquivo

    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )

    subprocess.run(
        [
            sys.executable,
            str(arquivo)
        ],
        check=True
    )


# =====================================================
# VALIDA DEPENDÊNCIAS AO INICIAR
# =====================================================
for arquivo in ARQUIVOS_OBRIGATORIOS:

    caminho = PASTA_SCRIPTS / arquivo

    if not caminho.exists():
        print(f"\nERRO: Arquivo não encontrado:")
        print(caminho)
        input("\nPressione ENTER para sair...")
        sys.exit(1)


# =====================================================
# INTERFACES OCIOSAS
# =====================================================
def interfaces_ociosas():

    print("\n[1/3] Coletando informações dos switches...")
    executar_script("salva_show_interfaces_link.py")

    print("\n[2/3] Gerando relatório...")
    executar_script("gerar_relatorio_interfaces.py")

    print("\n[3/3] Gerando scripts de configuração...")
    executar_script("gera_script_config_int.py")

    while True:

        opcao = input(
            "\nDeseja aplicar as configurações geradas nos switches? (S/N): "
        ).strip().upper()

        if opcao == "S":

            print("\nAplicando configurações...")
            executar_script("aplica_config.py")

            print("\nProcesso concluído.")
            break

        elif opcao == "N":

            print("\nConfigurações não aplicadas.")
            break

        else:

            print("Opção inválida. Digite S ou N.")


# =====================================================
# RELATÓRIO DE OCUPAÇÃO DOS SWITCHES
# =====================================================
def relatorio_ocupacao_switches():

    executar_script(
        "relatorio_ocupaçao_switches.py"
    )


# =====================================================
# GERENCIAR LISTA DE SWITCHES
# =====================================================
def gerenciar_lista_ip_switches():

    executar_script(
        "gerenciar_lista_ip_switches.py"
    )


# =====================================================
# MENU PRINCIPAL
# =====================================================
while True:

    print("\n==============================")
    print("      PORTAL AUTOMAÇÕES")
    print("==============================")
    print("1 - Gerenciar Lista de Switches")
    print("2 - Interfaces Ociosas")
    print("3 - Relatório Ocupação Switches")
    print("0 - Sair")
    print("==============================")

    opcao = input("Escolha uma opção: ").strip()

    if opcao == "1":

        try:
            gerenciar_lista_ip_switches()

        except Exception as e:
            print(f"\nErro: {e}")

    elif opcao == "2":

        try:
            interfaces_ociosas()

        except Exception as e:
            print(f"\nErro: {e}")

    elif opcao == "3":

        try:
            relatorio_ocupacao_switches()

        except Exception as e:
            print(f"\nErro: {e}")

    elif opcao == "0":

        print("\nEncerrando...")
        break

    else:

        print("\nOpção inválida.")