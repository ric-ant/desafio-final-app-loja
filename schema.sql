PRAGMA foreign_keys = ON;

-- Clientes: um cliente pode realizar vários pedidos (relacionamento 1:N).
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    sobrenome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    cidade TEXT NOT NULL,
    email TEXT UNIQUE,
    data_cadastro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Produtos: um produto pode aparecer em vários itens_pedido (relacionamento 1:N).
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL CHECK (preco >= 0),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    categoria TEXT NOT NULL
);

-- Pedidos: cada pedido pertence a um cliente; um cliente pode ter vários pedidos (1:N).
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    data_pedido TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('pendente', 'pago', 'enviado', 'cancelado')),
    valor_total REAL NOT NULL DEFAULT 0 CHECK (valor_total >= 0),
    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Itens_pedido: cada pedido possui vários itens (1:N) e cada produto pode estar em vários itens (1:N).
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
    subtotal REAL NOT NULL CHECK (subtotal >= 0 AND subtotal = quantidade * preco_unitario),
    FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Índices para as chaves estrangeiras.
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_id ON pedidos (cliente_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido_id ON itens_pedido (pedido_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_produto_id ON itens_pedido (produto_id);

-- Atualiza o total do pedido quando um item é incluído.
CREATE TRIGGER IF NOT EXISTS trg_itens_pedido_after_insert
AFTER INSERT ON itens_pedido
BEGIN
    UPDATE pedidos
    SET valor_total = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM itens_pedido
        WHERE pedido_id = NEW.pedido_id
    )
    WHERE id = NEW.pedido_id;
END;

-- Atualiza os totais do pedido de origem e do pedido de destino quando um item muda.
CREATE TRIGGER IF NOT EXISTS trg_itens_pedido_after_update
AFTER UPDATE ON itens_pedido
BEGIN
    UPDATE pedidos
    SET valor_total = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM itens_pedido
        WHERE pedido_id = OLD.pedido_id
    )
    WHERE id = OLD.pedido_id;

    UPDATE pedidos
    SET valor_total = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM itens_pedido
        WHERE pedido_id = NEW.pedido_id
    )
    WHERE id = NEW.pedido_id;
END;

-- Atualiza o total do pedido quando um item é removido.
CREATE TRIGGER IF NOT EXISTS trg_itens_pedido_after_delete
AFTER DELETE ON itens_pedido
BEGIN
    UPDATE pedidos
    SET valor_total = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM itens_pedido
        WHERE pedido_id = OLD.pedido_id
    )
    WHERE id = OLD.pedido_id;
END;

-- Resumo dos pedidos com a contagem de linhas de itens, inclusive pedidos sem itens.
CREATE VIEW IF NOT EXISTS vw_resumo_pedidos AS
SELECT
    p.id AS id_pedido,
    c.nome || ' ' || c.sobrenome AS nome_completo,
    c.cidade AS cidade,
    p.data_pedido AS data,
    p.status AS status,
    COUNT(ip.id) AS quantidade_itens,
    p.valor_total AS valor_total
FROM pedidos AS p
JOIN clientes AS c ON c.id = p.cliente_id
LEFT JOIN itens_pedido AS ip ON ip.pedido_id = p.id
GROUP BY p.id, c.nome, c.sobrenome, c.cidade, p.data_pedido, p.status, p.valor_total;
