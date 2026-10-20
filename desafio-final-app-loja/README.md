# desafio-final-app-loja

Aplicação de linha de comando que simula os relatórios de uma pequena loja virtual. Os dados ficam em um banco SQLite e são consultados com Python.

---

## Sobre o projeto

O sistema permite consultar informações da loja diretamente pelo terminal: preços, estoque, pedidos e itens por pedido. O banco de dados é criado e populado automaticamente na primeira execução, sem necessidade de configuração manual.

### Tecnologias

- Python 3.13+
- SQLite 3 (via módulo `sqlite3` da biblioteca padrão)

---

## Estrutura do projeto

```
desafio-final-app-loja/
├── Data/
│   ├── schema.sql       # Definição das tabelas, gatilhos e view
│   └── seed.sql         # Dados de exemplo (clientes, produtos, pedidos)
├── src/
│   ├── database.py      # Conexão, criação e carga inicial do banco
│   ├── queries.py       # Funções de consulta SQL
│   └── main.py          # Menu interativo (ponto de entrada)
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Documentação do projeto
```

---

## Pré-requisitos

- Python 3.13 ou superior instalado
- Nenhuma dependência externa — tudo usa a biblioteca padrão do Python

Verifique sua versão com:

```bash
python --version
```

---

## Como executar

### 1. Inicializar o banco de dados

Na primeira execução, crie as tabelas e popule com os dados de exemplo:

```bash
cd desafio-final-app-loja/src
python database.py
```

A saída exibe a contagem de registros e o resumo dos pedidos cadastrados, confirmando que o banco foi criado corretamente.

### 2. Iniciar a aplicação

```bash
python main.py
```

---

## Menu de consultas

Ao iniciar, o seguinte menu é exibido:

```
===== LOJA - CONSULTAS =====
1 - Média de preço dos produtos
2 - Saldo total de estoque
3 - Produtos e preços agrupados por categoria
4 - Contagem de pedidos por status
5 - Produtos por pedido
0 - Sair
```

### Opção 1 — Média de preço dos produtos

Calcula e exibe o preço médio de todos os produtos cadastrados.

### Opção 2 — Saldo total de estoque

Soma as unidades em estoque de todos os produtos e exibe o total.

### Opção 3 — Produtos agrupados por categoria

Exibe uma tabela com quantidade, preço médio, menor e maior preço por categoria, além de listar todos os produtos com seus preços.

### Opção 4 — Contagem de pedidos por status

Apresenta um submenu para escolher o status (`pago`, `pendente`, `enviado` ou `cancelado`) e retorna a quantidade de pedidos naquele estado.

### Opção 5 — Produtos por pedido

Lista os pedidos disponíveis e, após o usuário informar um ID, exibe todos os produtos daquele pedido com quantidade, preço unitário e subtotal.

---

## Banco de dados

O arquivo `src/loja.db` é gerado automaticamente na primeira execução do `database.py`. O esquema contém quatro tabelas principais:

| Tabela         | Descrição                                      |
|----------------|------------------------------------------------|
| `clientes`     | Dados cadastrais dos clientes                  |
| `produtos`     | Catálogo com preço, estoque e categoria        |
| `pedidos`      | Pedidos vinculados a clientes, com status      |
| `itens_pedido` | Itens de cada pedido com quantidade e subtotal |

Os totais dos pedidos são calculados automaticamente por gatilhos (_triggers_) definidos no `schema.sql`, garantindo consistência sem lógica extra no Python.

---

## Dados de exemplo

O `seed.sql` inclui:

- 10 clientes de diferentes cidades brasileiras
- 11 produtos em duas categorias: _Tênis e Calçados_ e _Vestuário_
- 5 pedidos com status variados (`pendente`, `pago`, `enviado`, `cancelado`)
- 16 itens de pedido distribuídos entre os pedidos
