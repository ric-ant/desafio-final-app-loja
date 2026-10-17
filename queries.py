import sqlite3

from database import conectar


STATUS_VALIDOS = ("pago", "pendente", "enviado", "cancelado")


def contar_pedidos_por_status(conn: sqlite3.Connection, status: str) -> int:
    """Retorna a quantidade de pedidos que possuem o status informado."""
    if status not in STATUS_VALIDOS:
        raise ValueError(
            f"Status inválido: {status!r}. "
            f"Escolha um destes: {', '.join(STATUS_VALIDOS)}."
        )

    resultado = conn.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?",
        (status,),
    ).fetchone()
    return int(resultado[0])


def media_preco_produtos(conn: sqlite3.Connection) -> float:
    """Retorna a média dos preços dos produtos, arredondada para duas casas."""
    resultado = conn.execute(
        "SELECT COALESCE(AVG(preco), 0) FROM produtos"
    ).fetchone()
    return round(float(resultado[0]), 2)


def saldo_total_estoque(conn: sqlite3.Connection) -> int:
    """Retorna a soma das unidades em estoque de todos os produtos."""
    resultado = conn.execute(
        "SELECT COALESCE(SUM(estoque), 0) FROM produtos"
    ).fetchone()
    return int(resultado[0])


def produtos_por_categoria(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Retorna estatísticas e nomes com preços dos produtos agrupados por categoria."""
    return conn.execute(
        """
        SELECT
            categoria,
            COUNT(*) AS quantidade_produtos,
            AVG(preco) AS preco_medio,
            MIN(preco) AS menor_preco,
            MAX(preco) AS maior_preco,
            GROUP_CONCAT(
                nome || ' (R$ ' || REPLACE(PRINTF('%.2f', preco), '.', ',') || ')',
                ' | '
            ) AS produtos_e_precos
        FROM produtos
        GROUP BY categoria
        ORDER BY categoria
        """
    ).fetchall()


def produtos_por_pedido(
    conn: sqlite3.Connection, pedido_id: int
) -> list[sqlite3.Row]:
    """Retorna os produtos, quantidades e valores do pedido informado."""
    return conn.execute(
        """
        SELECT
            p.id AS id_pedido,
            c.nome || ' ' || c.sobrenome AS cliente,
            pr.nome AS produto,
            ip.quantidade,
            ip.preco_unitario,
            ip.subtotal
        FROM pedidos AS p
        JOIN clientes AS c ON c.id = p.cliente_id
        JOIN itens_pedido AS ip ON ip.pedido_id = p.id
        JOIN produtos AS pr ON pr.id = ip.produto_id
        WHERE p.id = ?
        ORDER BY pr.nome
        """,
        (pedido_id,),
    ).fetchall()


def _formatar_moeda(valor: float) -> str:
    """Formata um valor monetário no padrão brasileiro."""
    valor_formatado = f"{valor:,.2f}"
    return valor_formatado.translate(str.maketrans({",": ".", ".": ","}))


def _exibir_menu_principal() -> None:
    """Exibe as opções disponíveis para executar consultas da loja."""
    print(
        "\n===== LOJA - CONSULTAS =====\n"
        "1 - Média de preço dos produtos\n"
        "2 - Saldo total de estoque\n"
        "3 - Produtos e preços agrupados por categoria\n"
        "4 - Contagem de pedidos por status\n"
        "5 - Produtos por pedido\n"
        "0 - Sair"
    )


def _pausar() -> None:
    """Aguarda o usuário antes de retornar ao menu principal."""
    input("Pressione Enter para continuar...")


def _opcao_media_preco(conn: sqlite3.Connection) -> None:
    """Consulta e exibe o preço médio dos produtos."""
    media = media_preco_produtos(conn)
    print(f"Preço médio dos produtos: R$ {_formatar_moeda(media)}")


def _opcao_saldo_estoque(conn: sqlite3.Connection) -> None:
    """Consulta e exibe o saldo total de estoque."""
    estoque = saldo_total_estoque(conn)
    print(f"Saldo total de estoque: {estoque} unidades")


def _opcao_produtos_por_categoria(conn: sqlite3.Connection) -> None:
    """Consulta e exibe os produtos agrupados por categoria em uma tabela."""
    categorias = produtos_por_categoria(conn)
    cabecalho = (
        f"{'Categoria':<22} {'Quantidade':>10} {'Preço médio':>14} "
        f"{'Menor preço':>14} {'Maior preço':>14}  Produtos"
    )
    print(cabecalho)
    print("-" * len(cabecalho))
    for categoria in categorias:
        print(
            f"{categoria['categoria']:<22.22} "
            f"{categoria['quantidade_produtos']:>10} "
            f"R$ {_formatar_moeda(float(categoria['preco_medio'])):>11} "
            f"R$ {_formatar_moeda(float(categoria['menor_preco'])):>11} "
            f"R$ {_formatar_moeda(float(categoria['maior_preco'])):>11}  "
            f"{categoria['produtos_e_precos']}"
        )


def _opcao_produtos_por_pedido(conn: sqlite3.Connection) -> None:
    """Pede um ID de pedido e exibe os produtos associados a ele."""
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


def _escolher_status() -> str | None:
    """Exibe o submenu e retorna um status válido ou None para voltar."""
    while True:
        print("Escolha o status do pedido:")
        for numero, status in enumerate(STATUS_VALIDOS, start=1):
            print(f"{numero} - {status}")
        print("0 - Voltar")

        opcao = input("Opção: ").strip()
        if opcao == "0":
            return None
        if opcao.isdigit() and 1 <= int(opcao) <= len(STATUS_VALIDOS):
            return STATUS_VALIDOS[int(opcao) - 1]
        print("Opção inválida, tente novamente.\n")


def _opcao_pedidos_por_status(conn: sqlite3.Connection) -> bool:
    """Consulta a contagem por status; retorna False se o usuário optar por voltar."""
    status = _escolher_status()
    if status is None:
        return False
    quantidade = contar_pedidos_por_status(conn, status)
    print(f"Pedidos com status '{status}': {quantidade}")
    return True


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
            if opcao == "4":
                if not _opcao_pedidos_por_status(conn):
                    continue
            elif opcao == "1":
                _opcao_media_preco(conn)
            elif opcao == "2":
                _opcao_saldo_estoque(conn)
            elif opcao == "3":
                _opcao_produtos_por_categoria(conn)
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
