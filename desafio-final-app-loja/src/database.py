import sqlite3
import sys
from pathlib import Path


PASTA_SCRIPT = Path(__file__).resolve().parent
PASTA_DATA = PASTA_SCRIPT.parent / "Data"
CAMINHO_BANCO = PASTA_SCRIPT / "loja.db"
CAMINHO_SCHEMA = PASTA_DATA / "schema.sql"
CAMINHO_SEED = PASTA_DATA / "seed.sql"


def conectar():
    """Abre o banco loja.db com chaves estrangeiras ativadas."""
    conn = sqlite3.connect(CAMINHO_BANCO)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ler_arquivo(caminho):
    """Lê um arquivo SQL em UTF-8 ou informa claramente se ele não existir."""
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {caminho.name}")
    return caminho.read_text(encoding="utf-8")


def _executar_script(conn, caminho):
    """Executa um script SQL dentro de uma transação e confirma as alterações."""
    conteudo = _ler_arquivo(caminho)
    try:
        conn.executescript(f"BEGIN;\n{conteudo}\nCOMMIT;")
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise


def criar_tabelas(conn):
    """Cria as tabelas, os gatilhos e a view definidos em schema.sql."""
    _executar_script(conn, CAMINHO_SCHEMA)


def popular_tabelas(conn):
    """Insere os dados de exemplo somente quando a tabela clientes está vazia."""
    try:
        clientes_existentes = conn.execute(
            "SELECT COUNT(*) FROM clientes"
        ).fetchone()[0]
        if clientes_existentes == 0:
            _executar_script(conn, CAMINHO_SEED)
    except sqlite3.Error:
        conn.rollback()
        raise



def verificar_dados(conn):
    """Exibe as contagens, o resumo dos pedidos e valida os totais."""
    tabelas = ("clientes", "produtos", "pedidos", "itens_pedido")
    print("Contagem de registros:")
    for tabela in tabelas:
        quantidade = conn.execute(
            f"SELECT COUNT(*) FROM {tabela}"
        ).fetchone()[0]
        print(f"  {tabela}: {quantidade}")

    print("\nResumo dos pedidos:")
    pedidos = conn.execute("SELECT * FROM vw_resumo_pedidos").fetchall()
    if pedidos:
        print(
            f"{'ID':>3}  {'Cliente':<28} {'Cidade':<18} "
            f"{'Data':<19} {'Status':<10} {'Itens':>5} {'Total':>10}"
        )
        for pedido in pedidos:
            print(
                f"{pedido['id_pedido']:>3}  "
                f"{pedido['nome_completo']:<28.28} "
                f"{pedido['cidade']:<18.18} "
                f"{pedido['data']:<19} "
                f"{pedido['status']:<10} "
                f"{pedido['quantidade_itens']:>5} "
                f"R$ {pedido['valor_total']:>7.2f}"
            )
    else:
        print("  Nenhum pedido cadastrado.")

    divergencias = conn.execute(
        """
        SELECT
            p.id,
            p.valor_total,
            COALESCE(SUM(ip.subtotal), 0) AS soma_subtotais
        FROM pedidos AS p
        LEFT JOIN itens_pedido AS ip ON ip.pedido_id = p.id
        GROUP BY p.id, p.valor_total
        HAVING ABS(p.valor_total - COALESCE(SUM(ip.subtotal), 0)) > 0.000000001
        ORDER BY p.id
        """
    ).fetchall()
    if divergencias:
        print("\nAVISO: há divergência entre o total do pedido e a soma dos itens:")
        for divergencia in divergencias:
            print(
                f"  Pedido {divergencia['id']}: "
                f"total R$ {divergencia['valor_total']:.2f}, "
                f"soma dos itens R$ {divergencia['soma_subtotais']:.2f}"
            )
    else:
        print("\nValidação dos totais: todos os pedidos correspondem à soma dos itens.")


def main():
    """Executa a inicialização, a carga de dados e a verificação do banco."""
    argumentos = sys.argv[1:]
    if argumentos:
        print("Uso: python database.py")
        return 2

    conn = None
    try:
        conn = conectar()
        criar_tabelas(conn)
        popular_tabelas(conn)
        verificar_dados(conn)
        return 0
    except FileNotFoundError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        if conn is not None:
            conn.rollback()
        return 1
    except sqlite3.Error as erro:
        print(f"Erro no banco de dados SQLite: {erro}", file=sys.stderr)
        if conn is not None:
            conn.rollback()
        return 1
    except OSError as erro:
        print(f"Erro ao acessar um arquivo do banco de dados: {erro}", file=sys.stderr)
        return 1
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
