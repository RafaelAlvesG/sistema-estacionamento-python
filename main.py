import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF



# Conexão com o banco de dados e criação da tabela
conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

# Tabela de clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    placa TEXT NOT NULL UNIQUE
)
""")

# Tabela de Movimentação
cursor.execute("""
CREATE TABLE IF NOT EXISTS movimentacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT NOT NULL UNIQUE,
    data_entrada TEXT,
    hora_entrada TEXT,
    data_saida TEXT,
    hora_saida TEXT,
    valor_calculado REAL DEFAULT 0,
    pendencia TEXT DEFAULT 'Não',
    acessos INTEGER DEFAULT 0,
    valor_ganhado REAL,
    FOREIGN KEY (placa) REFERENCES users(placa)
)
""")

# Faz commit das alterações no banco de dados
conexao.commit()


# Constante do valor cobrado por hora
VALOR_HORA = 7.0



# ===========================================================================================================
# Backend
# ===========================================================================================================



# Funçao de Cadastro de Clientes
def cadastrar():
    placa = entrada_placa_cad.get()
    nome = entrada_nome_cad.get()
    cpf = entrada_cpf_cad.get()

    # Tratamento de erro
    if not placa or not nome or not cpf:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
        return

    # Guarda valores dentro do banco de dados
    try:
        cursor.execute("""
        INSERT INTO users (nome, cpf, placa) VALUES (?, ?, ?)
        """, (nome, cpf, placa))
        
        cursor.execute("""
        INSERT INTO movimentacao (placa, pendencia) VALUES (?, 'Nao')
        """, (placa,))
        conexao.commit()

        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
        limpar_campos_cad()
        atualizar()

    # Tratamento de erro
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "CPF ou Placa já cadastrados.")



# Função de atualizar cadastro do Cliente
def atualizar_cadastro():
    placa = entrada_placa_cad.get()
    nome = entrada_nome_cad.get()
    cpf = entrada_cpf_cad.get()

    # Tratamento de erro
    if not placa:
        messagebox.showerror("Erro", "A Placa é obrigatória para atualizar o cadastro.")
        return

    # Tratamento de erro
    cursor.execute("SELECT * FROM users WHERE placa = ?", (placa,))
    if not cursor.fetchone():
        messagebox.showerror("Erro", "Veículo não encontrado.")
        return

    # Se estiver escrito atualizar
    if nome and cpf:
        cursor.execute("UPDATE users SET nome = ?, cpf = ? WHERE placa = ?", (nome, cpf, placa))
    elif nome:
        cursor.execute("UPDATE users SET nome = ? WHERE placa = ?", (nome, placa))
    elif cpf:
        cursor.execute("UPDATE users SET cpf = ? WHERE placa = ?", (cpf, placa))
    else:
        messagebox.showerror("Erro", "Preencha o Nome ou CPF para atualizar.")
        return

    # Faz commit das alterações
    conexao.commit()
    messagebox.showinfo("Sucesso", "Cadastro atualizado com sucesso!")
    limpar_campos_cad()
    atualizar()


# Função de Excluir Cadastro de Cliente
def excluir_cadastro():
    placa = entrada_placa_cad.get()
    
    # Tratamento de erro
    if not placa:
        messagebox.showerror("Erro", "A Placa é obrigatória para excluir o cadastro.")
        return

    # Busca valores no banco de dados
    cursor.execute("SELECT pendencia FROM movimentacao WHERE placa = ?", (placa,))
    registro = cursor.fetchone()
    
    # Tratamento de erro
    if not registro:
        messagebox.showerror("Erro", "Veículo não encontrado.")
        return
        
    if registro[0] == 'Sim':
        messagebox.showerror("Erro", "Não é possível excluir. O veículo possui pendências de pagamento.")
        return

    # Confirmação antes de excluir
    resposta = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o cadastro da placa {placa}?")
    if resposta:
        # Apaga os registros do banco de dados
        cursor.execute("DELETE FROM movimentacao WHERE placa = ?", (placa,))
        cursor.execute("DELETE FROM users WHERE placa = ?", (placa,))
        
        # Faz commit das alterações
        conexao.commit()
        
        messagebox.showinfo("Sucesso", "Cadastro excluído com sucesso!")
        limpar_campos_cad()
        atualizar()



# Função para limpar os campos de cadastro
def limpar_campos_cad():
    entrada_placa_cad.delete(0, tk.END)
    entrada_nome_cad.delete(0, tk.END)
    entrada_cpf_cad.delete(0, tk.END)



# Função para registrar a entrada do veículo
def entrada():
    placa = entrada_placa_mov.get()
    
    # Tratamento de erro
    if not placa:
        messagebox.showerror("Erro", "O campo Placa deve ser preenchido.")
        return

    # Busca valores no banco de dados
    cursor.execute("SELECT data_entrada FROM movimentacao WHERE placa = ?", (placa,))
    registro = cursor.fetchone()

    # Tratamento de erro
    if registro is None:
        messagebox.showerror("Erro", "Veículo não encontrado.")
        return

    banco = registro[0]
    
    # Tratamento de erro
    if banco is not None:
        messagebox.showerror("Erro", "Veículo já registrado como entrada. Registre a saída ou pague a pendência primeiro.")
        return

    # Guarda a data e hora atual
    agora = datetime.now()
    data_entrada = agora.strftime("%d/%m/%Y")
    hora_entrada = agora.strftime("%H:%M")

    # Atualiza valores dentro do banco de dados
    cursor.execute("""
    UPDATE movimentacao
    SET data_entrada = ?, hora_entrada = ? WHERE placa = ?
    """, (data_entrada, hora_entrada, placa))
    
    
    # Faz commit das alterações
    conexao.commit()

    messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
    entrada_placa_mov.delete(0, tk.END)
    atualizar()



# Função para registrar a saída do veículo e calcular os valores
def saida():
    placa = entrada_placa_mov.get()
    agora = datetime.now()
    data_saida = agora.strftime("%d/%m/%Y")
    hora_saida = agora.strftime("%H:%M")

    # Tratamento de erro
    if not placa:
        messagebox.showerror("Erro", "O campo Placa deve ser preenchido.")
        return

    # Busca valores no banco de dados
    cursor.execute("SELECT data_entrada, hora_entrada, pendencia FROM movimentacao WHERE placa = ? AND data_saida IS NULL AND data_entrada IS NOT NULL", (placa,))
    registro = cursor.fetchone()
    
    # Tratamento de erro
    if not registro:
        messagebox.showerror("Erro", "Veículo não encontrado, não deu entrada ou já registrou saída.")
        return
    
    if registro[2] == 'Sim':
        messagebox.showerror("Erro", "Este veículo já possui uma saída registrada e está com pagamento pendente.")
        return

    # Formata a data e hora para calcularmos os valores
    data_entrada_str = registro[0]
    hora_entrada_str = registro[1]
    data_entrada = datetime.strptime(data_entrada_str + " " + hora_entrada_str, "%d/%m/%Y %H:%M")
    data_saida_dt = datetime.strptime(data_saida + " " + hora_saida, "%d/%m/%Y %H:%M")
    
        # Calcula os valores baseados nas horas
    horas = (data_saida_dt - data_entrada).total_seconds() / 3600
    if horas < 0: horas = 0
    valores_calculados = horas * VALOR_HORA

    # Atualiza valores dentro do banco de dados
    cursor.execute("""
    UPDATE movimentacao
    SET data_saida = ?, hora_saida = ?, valor_calculado = ?, pendencia = 'Sim'
    WHERE placa = ?
    """, (data_saida, hora_saida, valores_calculados, placa))
    
    # Faz commit das alterações
    conexao.commit()

    entrada_placa_mov.delete(0, tk.END)
    messagebox.showinfo("Saída registrada com sucesso!", f"Valor a pagar: R$ {valores_calculados:.2f}")
    atualizar()



# Função para atualizar a lista de clientes na tela
def atualizar():
    texto_clientes.config(state=tk.NORMAL)
    texto_clientes.delete(1.0, tk.END)

    # Busca valores no banco de dados
    cursor.execute("SELECT * FROM users, movimentacao WHERE users.placa = movimentacao.placa")
    veiculos = cursor.fetchall()
   
    # Verificação se não há clientes
    if not veiculos:
        texto_clientes.insert(tk.END, "Nenhum veículo cadastrado.\n")
        texto_clientes.config(state=tk.DISABLED)
        return

    # Escreve a lista de todos os clientes no campo de texto
    for veiculo in veiculos:
        info = f"ID: {veiculo[0]} | Cliente: {veiculo[1]} | Placa: {veiculo[3]} | CPF: {veiculo[2]} | Pendência: {veiculo[11]}\n"
        texto_clientes.insert(tk.END, info)
    
    texto_clientes.config(state=tk.DISABLED)



# Função para buscar pendências de pagamento
def buscar_pendencia():
    placa = entrada_placa_pag.get()
    
    # Tratamento de erro
    if not placa:
        messagebox.showerror("Erro", "Informe a placa.")
        return
        
    # Busca valores no banco de dados
    cursor.execute("SELECT id, valor_calculado FROM movimentacao WHERE placa = ? AND pendencia = 'Sim'", (placa,))
    registros = cursor.fetchall()
    texto_pagamento.config(state=tk.NORMAL)
    texto_pagamento.delete(1.0, tk.END)
    
    # Se não tiver registros com pendências
    if not registros:
        texto_pagamento.insert(tk.END, "Nenhuma pendência encontrada para esta placa.")
    else:
        # Se existem pendências, listamos para o usuário
        for reg in registros:
            texto_pagamento.insert(tk.END, f"ID Movimentação: {reg[0]} | Valor: R$ {reg[1]:.2f}\n")
            
    texto_pagamento.config(state=tk.DISABLED)



# Função para registrar o pagamento de uma pendência
def pagar_pendencia():
    placa = entrada_placa_pag.get()
    
    # Tratamento de erro
    if not placa:
        messagebox.showerror("Erro", "Informe a placa.")
        return
        
    # Busca valores no banco de dados
    cursor.execute("SELECT valor_calculado, valor_ganhado, acessos FROM movimentacao WHERE placa = ? AND pendencia = 'Sim'", (placa,))
    registro = cursor.fetchone()
    
    # Se existe o registro
    if registro:
        valor_calc = registro[0] or 0
        valor_ganho = registro[1] or 0
        acessos = registro[2] or 0
        
        # Calcula os novos valores e quantidades de acessos do cliente
        novo_valor_ganho = valor_ganho + valor_calc
        novos_acessos = acessos + 1
        
        # Atualiza valores dentro do banco de dados, zerando pendencias e atualizando historico de pagamentos
        cursor.execute("""
            UPDATE movimentacao 
            SET pendencia = 'Nao', 
                valor_ganhado = ?, 
                acessos = ?,
                hora_entrada = NULL, 
                hora_saida = NULL, 
                data_entrada = NULL, 
                data_saida = NULL, 
                valor_calculado = 0
            WHERE placa = ? AND pendencia = 'Sim'
        """, (novo_valor_ganho, novos_acessos, placa))
        
        # Faz commit das alterações
        conexao.commit()
        
        messagebox.showinfo("Sucesso", "Pagamento registrado com sucesso!")
        buscar_pendencia()
        atualizar()
    else:
        # Quando não tem pendência
        messagebox.showinfo("Aviso", "Nenhuma pendência para pagar.")
    


# Função para gerar relatório de clientes cadastrados
def relatorio_clientes():
    texto_relatorio.config(state=tk.NORMAL)
    texto_relatorio.delete(1.0, tk.END)
    
    # Busca valores no banco de dados
    cursor.execute("SELECT nome, cpf, placa FROM users")
    for r in cursor.fetchall():
        texto_relatorio.insert(tk.END, f"Nome: {r[0]} | CPF: {r[1]} | Placa: {r[2]}\n")
        
    texto_relatorio.config(state=tk.DISABLED)



# Função para gerar relatório de veículos com pagamento em aberto
def relatorio_aberto():
    texto_relatorio.config(state=tk.NORMAL)
    texto_relatorio.delete(1.0, tk.END)
    
    # Busca valores no banco de dados
    cursor.execute("SELECT placa, data_entrada, valor_calculado FROM movimentacao WHERE pendencia = 'Sim' AND data_entrada IS NOT NULL")
    for r in cursor.fetchall():
        texto_relatorio.insert(tk.END, f"Placa: {r[0]} | Entrada: {r[1]} | Valor: R$ {r[2]:.2f}\n")
        
    texto_relatorio.config(state=tk.DISABLED)



# Função para gerar relatório do total recebido
def relatorio_recebimentos():
    texto_relatorio.config(state=tk.NORMAL)
    texto_relatorio.delete(1.0, tk.END)
    
    # Busca a soma dos valores recebidos no banco de dados
    cursor.execute("SELECT SUM(valor_ganhado) FROM movimentacao WHERE valor_ganhado > 0")
    resultado_total = cursor.fetchone()
    total_geral = resultado_total[0] if resultado_total[0] is not None else 0
    
    # Busca valores no banco de dados
    cursor.execute("SELECT placa, valor_ganhado FROM movimentacao WHERE valor_ganhado > 0")
    for r in cursor.fetchall():
        texto_relatorio.insert(tk.END, f"Placa: {r[0]} | Total Recebido: R$ {r[1]:.2f}\n")
        
    texto_relatorio.insert(tk.END, f"\nTotal Geral Recebido: R$ {total_geral:.2f}\n")
    texto_relatorio.config(state=tk.DISABLED)



# Função para gerar relatório dos 5 clientes com mais acessos
def relatorio_top5():
    texto_relatorio.config(state=tk.NORMAL)
    texto_relatorio.delete(1.0, tk.END)
    
    # Busca valores no banco de dados
    cursor.execute("""
        SELECT users.nome, movimentacao.placa, movimentacao.acessos
        FROM movimentacao
        JOIN users ON users.placa = movimentacao.placa
        WHERE movimentacao.acessos > 0
        ORDER BY movimentacao.acessos DESC
        LIMIT 5
    """)
    for r in cursor.fetchall():
        texto_relatorio.insert(tk.END, f"Cliente: {r[0]} | Placa: {r[1]} | Acessos: {r[2]}\n")
        
    texto_relatorio.config(state=tk.DISABLED)




# Função para gerar PDF do relatório exibido
def gerar_pdf():

    # Gera um arquivo PDF com o conteúdo atualmente exibido no campo de relatório.
    texto = texto_relatorio.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showwarning("Aviso", "Não há relatório para exportar. Gere um relatório antes de salvar o PDF.")
        return

    # Escolher local para salvar
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Arquivos PDF", "*.pdf")],
        title="Salvar PDF"
    )
    if not caminho_arquivo:
        return  # Usuário cancelou

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, texto)
        pdf.output(caminho_arquivo)
        messagebox.showinfo("Sucesso", f"PDF salvo em:\n{caminho_arquivo}")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível gerar o PDF:\n{e}")



# Função para verificar o login
def verificar_login():
    usuario = entrada_usuario.get()
    senha = entrada_senha.get()
    
    if usuario == "admin" and senha == "123":
        # Remove a tela de login
        frame_login.destroy()
        # Mostra o painel com as abas do sistema
        abas.pack(fill="both", expand=True, padx=15, pady=15)
        messagebox.showinfo("Login", "Login realizado com sucesso!")
    else:
        messagebox.showerror("Erro de Login", "Usuário ou senha incorretos!")



# ===========================================================================================================
# Frontend
# ===========================================================================================================

# Criação da janela principal
janela = tk.Tk()
janela.title("Controle de Estacionamento")
janela.state('zoomed') 
janela.geometry("900x550")
janela.configure(bg="#f0f0f0")

# Estilo para as abas e botões
style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background="#f0f0f0")
style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 5])
style.map("TNotebook.Tab", background=[("selected", "#4CAF50")], foreground=[("selected", "white")])

abas = ttk.Notebook(janela)
# Não usamos o "abas.pack(...)" aqui ainda, só vamos abrir isso depois do login.

# ===========================================================================================================
# Sistema de Login (Tela Inicial)
# ===========================================================================================================

frame_login = tk.Frame(janela, bg="#f0f0f0")
frame_login.pack(fill="both", expand=True)

frame_central_login = tk.Frame(frame_login, bg="#f0f0f0")
frame_central_login.pack(expand=True)

tk.Label(frame_central_login, text="SISTEMA DE LOGIN", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)
tk.Label(frame_central_login, text="Usuário:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
entrada_usuario = tk.Entry(frame_central_login, font=("Arial", 12), width=20)
entrada_usuario.pack(pady=5)

tk.Label(frame_central_login, text="Senha:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
entrada_senha = tk.Entry(frame_central_login, font=("Arial", 12), width=20, show="*")
entrada_senha.pack(pady=5)

botao_login = tk.Button(frame_central_login, text="Entrar", command=verificar_login, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=15)
botao_login.pack(pady=20)

fonte_padrao = ("Arial", 11)

# ===========================================================================================================
# Abas do Sistema (Carregadas em segundo plano)
# ===========================================================================================================

# Aba de cadastro
aba_clientes = ttk.Frame(abas)
abas.add(aba_clientes, text="Cadastro de Clientes")

frame_form_cad = tk.Frame(aba_clientes, pady=10)
frame_form_cad.pack(fill="x", padx=20)

tk.Label(frame_form_cad, text="Placa:", font=fonte_padrao).grid(row=0, column=0, sticky="w", padx=10, pady=5)
entrada_placa_cad = tk.Entry(frame_form_cad, width=30, font=fonte_padrao)
entrada_placa_cad.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_form_cad, text="Nome do Cliente:", font=fonte_padrao).grid(row=1, column=0, sticky="w", padx=10, pady=5)
entrada_nome_cad = tk.Entry(frame_form_cad, width=30, font=fonte_padrao)
entrada_nome_cad.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_form_cad, text="CPF:", font=fonte_padrao).grid(row=2, column=0, sticky="w", padx=10, pady=5)
entrada_cpf_cad = tk.Entry(frame_form_cad, width=30, font=fonte_padrao)
entrada_cpf_cad.grid(row=2, column=1, padx=10, pady=5)

frame_botoes_cad = tk.Frame(aba_clientes)
frame_botoes_cad.pack(pady=10)

botao_cadastrar = tk.Button(frame_botoes_cad, command=cadastrar, text="Registrar Novo", bg="#4CAF50", fg="white", font=fonte_padrao, width=15)
botao_cadastrar.grid(row=0, column=0, padx=5)

botao_atualizar_cad = tk.Button(frame_botoes_cad, command=atualizar_cadastro, text="Atualizar Cadastro", bg="#2196F3", fg="white", font=fonte_padrao, width=15)
botao_atualizar_cad.grid(row=0, column=1, padx=5)

botao_excluir_cad = tk.Button(frame_botoes_cad, command=excluir_cadastro, text="Excluir Cadastro", bg="#f44336", fg="white", font=fonte_padrao, width=15)
botao_excluir_cad.grid(row=0, column=2, padx=5)

botao_listar = tk.Button(frame_botoes_cad, text="Atualizar Lista", bg="#607D8B", fg="white", font=fonte_padrao, width=15, command=atualizar)
botao_listar.grid(row=0, column=3, padx=5)

texto_clientes = tk.Text(aba_clientes, height=15, width=100, font=("Consolas", 10), state="disabled", bg="#ffffff", relief="solid", borderwidth=1)
texto_clientes.pack(pady=10, padx=20)
atualizar()


# Aba entrada e saida de veículos
aba_entrada_saida = ttk.Frame(abas)
abas.add(aba_entrada_saida, text="Entrada/Saída")

frame_mov = tk.Frame(aba_entrada_saida, pady=20)
frame_mov.pack()

tk.Label(frame_mov, text="Placa do Veículo:", font=fonte_padrao).grid(row=0, column=0, sticky="w", padx=10, pady=10)
entrada_placa_mov = tk.Entry(frame_mov, width=30, font=fonte_padrao)
entrada_placa_mov.grid(row=0, column=1, padx=10, pady=10)

frame_botoes_mov = tk.Frame(aba_entrada_saida)
frame_botoes_mov.pack(pady=20)

botao_entrada_mov = tk.Button(frame_botoes_mov, command=entrada, text="Registrar Entrada", bg="#4CAF50", fg="white", font=fonte_padrao, width=20, height=2)
botao_entrada_mov.grid(row=0, column=0, padx=10)

botao_saida_mov = tk.Button(frame_botoes_mov, command=saida, text="Registrar Saída + Calcular", bg="#f44336", fg="white", font=fonte_padrao, width=20, height=2)
botao_saida_mov.grid(row=0, column=1, padx=10)



# Aba de Pagamento
aba_pagamento = ttk.Frame(abas)
abas.add(aba_pagamento, text="Pagamento")

frame_pag = tk.Frame(aba_pagamento, pady=20)
frame_pag.pack()

tk.Label(frame_pag, text="Placa do Veículo:", font=fonte_padrao).grid(row=0, column=0, sticky="w", padx=10, pady=10)
entrada_placa_pag = tk.Entry(frame_pag, width=30, font=fonte_padrao)
entrada_placa_pag.grid(row=0, column=1, padx=10, pady=10)

frame_botoes_pag = tk.Frame(aba_pagamento)
frame_botoes_pag.pack(pady=10)

botao_buscar_pag = tk.Button(frame_botoes_pag, text="Buscar Pendências", command=buscar_pendencia, bg="#2196F3", fg="white", font=fonte_padrao, width=20)
botao_buscar_pag.grid(row=0, column=0, padx=10)

botao_pagar = tk.Button(frame_botoes_pag, text="Registrar Pagamento", bg="#4CAF50", fg="white", command=pagar_pendencia, font=fonte_padrao, width=20)
botao_pagar.grid(row=0, column=1, padx=10)

texto_pagamento = tk.Text(aba_pagamento, height=12, width=80, font=("Consolas", 11), state="disabled", bg="#ffffff", relief="solid", borderwidth=1)
texto_pagamento.pack(pady=20)



# Aba de relatórios
aba_relatorios = ttk.Frame(abas)
abas.add(aba_relatorios, text="Relatórios")

frame_botoes_rel = tk.Frame(aba_relatorios, pady=20)
frame_botoes_rel.pack()

tk.Button(frame_botoes_rel, text="Clientes", command=relatorio_clientes, bg="#607D8B", fg="white", font=fonte_padrao, width=15).grid(row=0, column=0, padx=5)
tk.Button(frame_botoes_rel, text="Em Aberto", command=relatorio_aberto, bg="#FF9800", fg="white", font=fonte_padrao, width=15).grid(row=0, column=1, padx=5)
tk.Button(frame_botoes_rel, text="Recebimentos", command=relatorio_recebimentos, bg="#4CAF50", fg="white", font=fonte_padrao, width=15).grid(row=0, column=2, padx=5)
tk.Button(frame_botoes_rel, text="Top 5 Clientes", command=relatorio_top5, bg="#9C27B0", fg="white", font=fonte_padrao, width=15).grid(row=0, column=3, padx=5)


# Campo de texto para exibir relatórios
texto_relatorio = tk.Text(aba_relatorios, height=18, width=90, font=("Consolas", 11), state="disabled", bg="#ffffff", relief="solid", borderwidth=1)
texto_relatorio.pack(pady=10)

# Botão para exportar relatório em PDF
frame_pdf = tk.Frame(aba_relatorios)
frame_pdf.pack(pady=5)
botao_pdf = tk.Button(frame_pdf, text="Exportar Relatório em PDF", command=gerar_pdf, bg="#D32634", fg="white", font=fonte_padrao, width=30)
botao_pdf.pack()

# Mantém a janela aberta e interativa
janela.mainloop()

# Fecha a conexão com o banco de dados ao fechar a janela
conexao.close()
