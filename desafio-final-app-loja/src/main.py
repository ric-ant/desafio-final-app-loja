import sqlite3

from database import conectar
from queries import (
    contar_pedidos_por_status,
    media_preco_produtos,
    saldo_total_estoque,
    produtos_por_categoria,
    produtos_por_pedido,
)


STATUS_VALIDOS = ("pago", "pendente", "enviado", "cancelado")


def _formatar_moeda(valor: float) -> str:
    """Formata um valor monetário no padrão brasileiro."""
    valor_formatado = f"{valor:,.2f}"
    return valor_formatado.translate(str.maketrans({",": ".", ".": ","}))


def _pausar() -> None:
    """Aguarda o usuário antes de retornar ao menu principal."""
    input("\nPressione Enter para continuar...")


def _exibir_menu_principal() -> None:
    """Exibe as opções disponíveis."""
    print(
        "\n===== LOJA - CONSULTAS =====\n"
        "1 - Média de preço dos produtos\n"
        "2 - Saldo total de estoque\n"
        "3 - Produtos e preços agrupados por categoria\n"
        "4 - Contagem de pedidos por status\n"
        "5 - Produtos por pedido\n"
        "0 - Sair"
    )


# ── Opções do menu ────────────────────────────────────────────────────────────

def _opcao_media_preco(conn: sqlite3.Connection) -> None:
    media = media_preco_produtos(conn)
    print(f"Preço médio dos produtos: R$ {_formatar_moeda(media)}")


def _opcao_saldo_estoque(conn: sqlite3.Connection) -> None:
    estoque = saldo_total_estoque(conn)
    print(f"Saldo total de estoque: {estoque} unidades")


def _opcao_produtos_por_categoria(conn: sqlite3.Connection) -> None:
    categorias = produtos_por_categoria(conn)
    cabecalho = (
        f"{'Categoria':<22} {'Quantidade':>10} {'Preço médio':>14} "
        f"{'Menor preço':>14} {'Maior preço':>14}  Produtos"
    )
    print(cabecalho)
    print("-" * len(cabecalho))
    for cat in categorias:
        print(
            f"{cat['categoria']:<22.22} "
            f"{cat['quantidade_produtos']:>10} "
            f"R$ {_formatar_moeda(float(cat['preco_medio'])):>11} "
            f"R$ {_formatar_moeda(float(cat['menor_preco'])):>11} "
            f"R$ {_formatar_moeda(float(cat['maior_preco'])):>11}  "
            f"{cat['produtos_e_precos']}"
        )


def _escolher_status() -> str | None:
    """Exibe o submenu de status; retorna o status escolhido ou None para voltar."""
    while True:
        print("Escolha o status do pedido:")
        for numero, status in enumerate(STATUS_VALIDOS, start=1):
            print(f"  {numero} - {status}")
        print("  0 - Voltar")
        opcao = input("Opção: ").strip()
        if opcao == "0":
            return None
        if opcao.isdigit() and 1 <= int(opcao) <= len(STATUS_VALIDOS):
            return STATUS_VALIDOS[int(opcao) - 1]
        print("Opção inválida, tente novamente.\n")


def _opcao_pedidos_por_status(conn: sqlite3.Connection) -> bool:
    """Retorna False se o usuário optar por voltar."""
    status = _escolher_status()
    if status is None:
        return False
    quantidade = contar_pedidos_por_status(conn, status)
    print(f"Pedidos com status '{status}': {quantidade}")
    return True


def _opcao_produtos_por_pedido(conn: sqlite3.Connection) -> None:
    pedidos = conn.execute(
        """
        SELECT p.id, c.nome || ' ' || c.sobrenome AS cliente
        FROM pedidos AS p
        JOIN clientes AS c ON c.id = p.cliente_id
        ORDER BY p.id
        """
    ).fetchall()
    if not pedidos:
        print("Não há pedidos cadastrados.")
        return

    print("Pedidos disponíveis:")
    for pedido in pedidos:
        print(f"  {pedido['id']} - {pedido['cliente']}")

    ids_pedidos = {pedido["id"] for pedido in pedidos}
    while True:
        entrada = input("Digite o pedido_id (0 para voltar): ").strip()
        if entrada == "0":
            return
        if not entrada.isdigit() or int(entrada) not in ids_pedidos:
            print("ID de pedido inválido. Escolha um dos pedidos listados.")
            continue
        pedido_id = int(entrada)
        break

    itens = produtos_por_pedido(conn, pedido_id)
    if not itens:
        print(f"O pedido {pedido_id} não possui produtos.")
        return

    cabecalho = (
        f"{'Pedido':>6}  {'Cliente':<28} {'Produto':<44} "
        f"{'Qtd.':>4} {'Preço unitário':>16} {'Subtotal':>14}"
    )
    print(cabecalho)
    print("-" * len(cabecalho))
    for item in itens:
        print(
            f"{pedido_id:>6}  "
            f"{item['cliente']:<28.28} "
            f"{item['produto']:<44.44} "
            f"{item['quantidade']:>4} "
            f"R$ {_formatar_moeda(float(item['preco_unitario'])):>11} "
            f"R$ {_formatar_moeda(float(item['subtotal'])):>9}"
        )


# ── Ponto de entrada ──────────────────────────────────────────────────────────

def main() -> int:
    """Abre a conexão e mantém o menu interativo até o usuário sair."""
    conn = None
    try:
        conn = conectar()
        while True:
            _exibir_menu_principal()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "0":
                print("Encerrando...")
                return 0
            if opcao not in {"1", "2", "3", "4", "5"}:
                print("Opção inválida, tente novamente.")
                continue

            if opcao == "1":
                _opcao_media_preco(conn)
            elif opcao == "2":
                _opcao_saldo_estoque(conn)
            elif opcao == "3":
                _opcao_produtos_por_categoria(conn)
            elif opcao == "4":
                if not _opcao_pedidos_por_status(conn):
                    continue
            elif opcao == "5":
                _opcao_produtos_por_pedido(conn)

            _pausar()
    except sqlite3.Error as erro:
        print(f"Erro ao consultar o banco de dados SQLite: {erro}")
        return 1
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        return 0
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
