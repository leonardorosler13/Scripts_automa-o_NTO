from pathlib import Path
#PASTA_SCRIPTS = Path(r"C:\Automações\Cisco")
PASTA_SCRIPTS = Path(r"C:\Automações")
ARQUIVO_IPS = PASTA_SCRIPTS / "lista_ip_switches.txt"

def gerenciar_switches():

    while True:

        print("\n================================")
        print(" GERENCIAR LISTA DE SWITCHES")
        print("================================")

        if ARQUIVO_IPS.exists():
            with open(ARQUIVO_IPS, "r") as f:
                ips = [linha.strip() for linha in f if linha.strip()]
        else:
            ips = []

        if ips:
            for i, ip in enumerate(ips, start=1):
                print(f"{i:02d} - {ip}")
        else:
            print("Lista vazia.")

        print(f"\nTotal de IPs: {len(ips)}")

        print("\nA - Adicionar IP")
        print("R - Remover IP")
        print("L - Limpar Lista")
        print("V - Voltar")

        opcao = input("\nEscolha: ").upper().strip()

        if opcao == "A":

            novo_ip = input("Digite o IP: ").strip()

            if novo_ip and novo_ip not in ips:

                with open(ARQUIVO_IPS, "a") as f:
                    f.write(novo_ip + "\n")

                print("IP adicionado com sucesso.")

            else:
                print("IP já existe ou é inválido.")

        elif opcao == "R":

            numero = input("Número do IP para remover: ")

            if numero.isdigit():

                numero = int(numero)

                if 1 <= numero <= len(ips):

                    removido = ips.pop(numero - 1)

                    with open(ARQUIVO_IPS, "w") as f:
                        for ip in ips:
                            f.write(ip + "\n")

                    print(f"IP {removido} removido com sucesso.")

                else:
                    print("Número inválido.")

        elif opcao == "L":

            confirmar = input(
                "Apagar toda a lista? (S/N): "
            ).upper()

            if confirmar == "S":

                with open(ARQUIVO_IPS, "w") as f:
                    pass

                print("Lista limpa.")

        elif opcao == "V":

            break

        else:

            print("Opção inválida.")
            
if __name__ == "__main__":
    gerenciar_switches()