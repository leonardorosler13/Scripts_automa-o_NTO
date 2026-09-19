import subprocess

# Etapa 2
print("Executando coleta das interfaces...")
subprocess.run(["python", "salva_show_interfaces_link.py"], check=True)
print("Concluído!")

# Etapa 3
print("Gerando relatório...")
subprocess.run(["python", "gerar_relatorio_interfaces.py"], check=True)
print("Concluído!")

# Etapa 4
print("Gerando scripts de configuração...")
subprocess.run(["python", "gera_script_config_int.py"], check=True)

print("Processo finalizado com sucesso!")