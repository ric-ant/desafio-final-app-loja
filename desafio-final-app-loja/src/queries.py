import sqlite3


STATUS_VALIDOS = ("pago", "pendente", "enviado", "cancelado")


def contar_pedidos_por_status(conn: sqlite3.Connection, status: str) -> int:
    """Retorna a quantidade de pedidos que possuem o status informado."""
    if status not in STATUS_VALIDOS:
        raise ValueError(
            f"Status inválido: {status!r}. "
            f"Escolha um destes: {', '.join(STATUS_VALIDOS)}."
        )
    try:
        resultado = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?",
            (status,),
        ).fetchone()
        return int(resultado[0])
    except sqlite3.Error as erro:
        raise sqlite3.Error(f"Erro ao contar pedidos por status: {erro}") from erro


def media_preco_produtos(conn: sqlite3.Connection) -> float:
    """Retorna a média dos preços dos produtos, arredondada para duas casas."""
    try:
        resultado = conn.execute(
            "SELECT COALESCE(AVG(preco), 0) FROM produtos"
        ).fetchone()
        return round(float(resultado[0]), 2)
    except sqlite3.Error as erro:
        raise sqlite3.Error(f"Erro ao calcular média de preços: {erro}") from erro


def saldo_total_estoque(conn: sqlite3.Connection) -> int:
    """Retorna a soma das unidades em estoque de todos os produtos."""
    try:
        resultado = conn.execute(
            "SELECT COALESCE(SUM(estoque), 0) FROM produtos"
        ).fetchone()
        return int(resultado[0])
    except sqlite3.Error as erro:
        raise sqlite3.Error(f"Erro ao calcular saldo de estoque: {erro}") from erro


def produtos_por_categoria(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Retorna estatísticas e nomes com preços dos produtos agrupados por categoria."""
    try:
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
    except sqlite3.Error as erro:
        raise sqlite3.Error(f"Erro ao buscar produtos por categoria: {erro}") from erro


# Consulta a VIEW vw_pedidos_por_cliente criada em schema.sql
def pedidos_por_cliente(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Retorna os pedidos de cada cliente via vw_pedidos_por_cliente."""
    try:
        return conn.execute(
            "SELECT * FROM vw_pedidos_por_cliente"
        ).fetchall()
    except sqlite3.Error as erro:
        raise sqlite3.Error(f"Erro ao buscar pedidos por cliente: {erro}") from erro


def produtos_por_pedido(
    conn: sqlite3.Connection, pedido_id: int
) -> list[sqlite3.Row]:
    """Retorna os produtos, quantidades e valores do pedido informado."""
    try:
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
    except sqlite3.Error as erro:
        raise sqlite3.Error(f"Erro ao buscar produtos do pedido {pedido_id}: {erro}") from erro
