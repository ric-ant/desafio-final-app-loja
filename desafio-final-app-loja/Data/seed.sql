PRAGMA foreign_keys = ON;

-- Clientes brasileiros fictícios.
INSERT INTO clientes (id, nome, sobrenome, endereco, cidade, email, data_cadastro) VALUES
(1, 'Ana', 'Silva', 'Rua dos Andradas, 125', 'Porto Alegre', 'ana.silva@example.com', '2025-01-10 09:15:00'),
(2, 'Bruno', 'Oliveira', 'Avenida Paulista, 840', 'São Paulo', 'bruno.oliveira@example.com', '2025-01-12 11:30:00'),
(3, 'Camila', 'Souza', 'Rua XV de Novembro, 310', 'Curitiba', 'camila.souza@example.com', '2025-01-15 14:20:00'),
(4, 'Diego', 'Pereira', 'Rua Marquês do Herval, 72', 'Santo Ângelo', 'diego.pereira@example.com', '2025-01-18 08:45:00'),
(5, 'Eduarda', 'Costa', 'Avenida Atlântica, 1550', 'Rio de Janeiro', 'eduarda.costa@example.com', '2025-01-20 16:10:00'),
(6, 'Felipe', 'Almeida', 'Rua Bahia, 402', 'Belo Horizonte', 'felipe.almeida@example.com', '2025-01-23 10:05:00'),
(7, 'Gabriela', 'Rodrigues', 'Rua das Flores, 96', 'Florianópolis', 'gabriela.rodrigues@example.com', '2025-01-25 13:40:00'),
(8, 'Henrique', 'Ferreira', 'Avenida Brasil, 2201', 'Campinas', 'henrique.ferreira@example.com', '2025-01-28 17:25:00'),
(9, 'Isabela', 'Martins', 'Rua do Comércio, 518', 'Santa Maria', 'isabela.martins@example.com', '2025-02-01 09:50:00'),
(10, 'João', 'Barbosa', 'Rua General Osório, 144', 'Pelotas', 'joao.barbosa@example.com', '2025-02-04 12:35:00');

-- Produtos com preços em reais, estoque entre 10 e 100 e suas categorias.
INSERT INTO produtos (id, nome, descricao, preco, estoque, categoria) VALUES
(1, 'Tênis de Corrida Nike Downshifter 13', 'Tênis leve para corrida e caminhada.', 349.90, 45, 'Tênis e Calçados'),
(2, 'Tênis Casual Adidas Grand Court Base 2.0', 'Tênis casual com design clássico.', 299.99, 38, 'Tênis e Calçados'),
(3, 'Tênis Clássico All Star Converse Chuck Taylor', 'Tênis de lona com cano baixo.', 199.90, 52, 'Tênis e Calçados'),
(4, 'Bota Coturno de Couro Legítimo', 'Bota resistente de couro legítimo.', 249.00, 24, 'Tênis e Calçados'),
(5, 'Sandália Rasteira Feminina Anacapri', 'Sandália rasteira confortável.', 89.90, 60, 'Tênis e Calçados'),
(6, 'Calça Jeans Levi''s 501 Original', 'Calça jeans reta de estilo tradicional.', 399.90, 31, 'Vestuário'),
(7, 'Camiseta Básica 100% Algodão Premium', 'Camiseta macia de algodão premium.', 49.90, 100, 'Vestuário'),
(8, 'Blazer de Alfaiataria Feminino Estruturado', 'Blazer estruturado para ocasiões formais.', 189.90, 18, 'Vestuário'),
(9, 'Moletom Canguru Unissex com Capuz', 'Moletom confortável com bolso frontal.', 129.90, 42, 'Vestuário'),
(10, 'Vestido Midi Canelado com Fenda', 'Vestido midi canelado com fenda lateral.', 79.90, 27, 'Vestuário'),
(11, 'Jaqueta Corta-Vento Esportiva', 'Jaqueta leve para atividades ao ar livre.', 159.90, 36, 'Vestuário');

-- Cinco pedidos de clientes distintos, com datas e status variados; os gatilhos calcularão os totais.
INSERT INTO pedidos (id, cliente_id, data_pedido, status, valor_total) VALUES
(1, 2, '2025-03-02 10:15:00', 'pendente', 0),
(2, 4, '2025-03-05 14:40:00', 'pago', 0),
(3, 6, '2025-03-11 09:25:00', 'enviado', 0),
(4, 8, '2025-03-16 16:05:00', 'cancelado', 0),
(5, 10, '2025-03-22 11:50:00', 'pago', 0);

-- Itens dos pedidos: cada linha registra quantidade, preço vigente e subtotal correspondente.
INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario, subtotal) VALUES
(1, 1, 1, 349.90, 349.90),
(1, 7, 2, 49.90, 99.80),

(2, 2, 1, 299.99, 299.99),
(2, 6, 1, 399.90, 399.90),
(2, 9, 2, 129.90, 259.80),

(3, 3, 2, 199.90, 399.80),
(3, 5, 1, 89.90, 89.90),
(3, 11, 1, 159.90, 159.90),
(3, 10, 2, 79.90, 159.80),

(4, 4, 1, 249.00, 249.00),
(4, 8, 1, 189.90, 189.90),

(5, 1, 1, 349.90, 349.90),
(5, 2, 1, 299.99, 299.99),
(5, 7, 3, 49.90, 149.70),
(5, 10, 1, 79.90, 79.90),
(5, 11, 1, 159.90, 159.90);

-- Conferência dos totais calculados automaticamente pelos gatilhos.
SELECT * FROM vw_resumo_pedidos;
