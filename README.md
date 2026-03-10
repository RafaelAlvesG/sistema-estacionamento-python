# 🚗 Sistema de Controle de Estacionamento

Um aplicativo desktop simples desenvolvido em Python para gerenciar o fluxo de entrada e saída de veículos em um estacionamento, incluindo controle de pagamentos e relatórios básicos.

## Funcionalidades

- 🔒 **Sistema de Login:** Acesso restrito para segurança das informações do caixa (Usuário: `admin`, Senha: `123`);
- 📝 **Cadastro de Veículos e Clientes:** Registre a placa, nome e CPF.
- ⏱️ **Registro de Movimentação:** Marca entrada e calcula dinamicamente o tempo de permanência na saída do veículo.
- 💰 **Controle de Pagamentos:** Verifique e dê baixa nas pendências de clientes.
- 📊 **Relatórios em PDF:** Gere planilhas rápidas para acompanhar quem está devendo e quem frequenta o pátio.

## Como Executar

### Pré-Requisitos:
- **Python 3.x**
- As seguintes bibliotecas externas (para exportar relatórios para PDF e recursos adicionais):
```bash
pip install fpdf matplotlib
```

### Rodando o projeto:
Clone o repositório, navegue até a pasta pelo terminal e digite:
```bash
python main.py
```
O banco de dados (`banco.db`) usando **SQLite3** é construído automaticamente na primeira execução do código. Não é necessário configurar o banco previamente.

## Tecnologias Utilizadas
- **Python** no Backend da aplicação
- **Tkinter** para a Interface Gráfica (Frontend)
- **SQLite3** para armazenamento local e nativo dos dados