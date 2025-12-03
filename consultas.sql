-- Consulta 1: Linhas acessíveis em um bairro

-- Mostra todas as linhas ativas com ônibus acessíveis que passam por um bairro específico.
-- Inclui informações como tarifa, tempo de percurso e empresa responsável.

SELECT DISTINCT
    l.NOME_CODIGO,
    l.TARIFA,
    l.TEMPO_PERCURSO,
    e.NOME AS nome_empresa
FROM LINHA l
JOIN ONIBUS o
  ON o.NOME_CODIGO_LINHA = l.NOME_CODIGO
JOIN PONTO_PARADA p
  ON p.NOME_CODIGO_LINHA = l.NOME_CODIGO
JOIN EMPRESA_PUBLICA e
  ON l.CNPJ_EMPRESA_PUBLICA = e.CNPJ
WHERE o.ACESSIBILIDADE = 'S'
  AND p.BAIRRO ILIKE 'Centro'   -- Substitua pelo bairro desejado
  AND l.ATIVO = 'S'
ORDER BY l.NOME_CODIGO;


-- Consulta 2: Histórico de viagens de um cidadão

-- Retorna o número de viagens, custo total e tempo médio de deslocamento
-- para um cidadão em um período específico.

SELECT
    COUNT(*) AS quantidade_viagens,
    COALESCE(SUM(CUSTO_TOTAL), 0) AS custo_total,
    AVG(EXTRACT(EPOCH FROM (DATAHORA_FINAL - DATAHORA_INICIO)) / 60.0)
        AS tempo_medio_minutos
FROM VIAGEM
WHERE CPF_CIDADAO = '11111111111'            -- Substitua pelo CPF desejado
  AND DATAHORA_INICIO >= DATE '2025-11-01'   -- Data inicial do período
  AND DATAHORA_INICIO <  DATE '2025-12-01';  -- Data final 


-- Consulta 3: Linhas mais usadas por um cidadão

-- Lista as linhas mais utilizadas por um cidadão, ordenadas pela quantidade de viagens.

SELECT
    v.NOME_CODIGO_LINHA_EMBARQUE AS linha,
    COUNT(*)                     AS qtd_viagens
FROM VIAGEM v
WHERE v.CPF_CIDADAO = '11111111111'   -- Substitua pelo CPF desejado
GROUP BY v.NOME_CODIGO_LINHA_EMBARQUE
ORDER BY qtd_viagens DESC, linha;


-- Consulta 4: Rotas mais utilizadas entre bairros

-- Mostra os trajetos mais frequentes entre bairros de origem e destino.

SELECT
    pe.BAIRRO AS bairro_origem,
    pd.BAIRRO AS bairro_destino,
    COUNT(*)  AS qtd_viagens
FROM VIAGEM v
JOIN PONTO_PARADA pe
  ON v.NOME_CODIGO_LINHA_EMBARQUE = pe.NOME_CODIGO_LINHA
 AND v.NRO_PARADA_EMBARQUE        = pe.NRO_PARADA
JOIN PONTO_PARADA pd
  ON v.NOME_CODIGO_LINHA_DESEMBARQUE = pd.NOME_CODIGO_LINHA
 AND v.NRO_PARADA_DESEMBARQUE        = pd.NRO_PARADA
GROUP BY pe.BAIRRO, pd.BAIRRO
ORDER BY qtd_viagens DESC, bairro_origem, bairro_destino;


-- Consulta 5: Cidadãos que usaram todas as linhas de uma empresa

-- Encontra cidadãos que já viajaram em todas as linhas de uma empresa pública específica.

SELECT
    uc.CPF,
    uc.EMAIL
FROM USUARIO_CIDADAO uc
WHERE NOT EXISTS (
    -- Verifica se há alguma linha da empresa que o cidadão não utilizou
    SELECT 1
    FROM LINHA l
    WHERE l.CNPJ_EMPRESA_PUBLICA = '10101010000110'   -- Substitua pelo CNPJ da empresa
      AND NOT EXISTS (
          SELECT 1
          FROM VIAGEM v
          WHERE v.CPF_CIDADAO = uc.CPF
            AND v.NOME_CODIGO_LINHA_EMBARQUE = l.NOME_CODIGO
      )
);
