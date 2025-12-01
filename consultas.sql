

------------------------------------------------------------
-- 1) Linhas acessíveis em um bairro específico
--
-- Objetivo:
--   Listar todas as linhas ativas que possuem ônibus acessíveis
--   (ACESSIBILIDADE = 'S') e que atendem um determinado bairro,
--   considerando os pontos de parada dessa linha.
--
-- Operadores/recursos usados:
--   - JOIN entre LINHA, ONIBUS, PONTO_PARADA e EMPRESA_PUBLICA
--   - DISTINCT para evitar duplicação de linhas
--   - Filtro por bairro (ILIKE) e por status de linha (ATIVO = 'S')
------------------------------------------------------------

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
  AND p.BAIRRO ILIKE 'Centro'   -- trocar pelo bairro desejado
  AND l.ATIVO = 'S'
ORDER BY l.NOME_CODIGO;


------------------------------------------------------------
-- 2) Histórico de viagens de um cidadão em um período
--
-- Objetivo:
--   Calcular, para um cidadão específico em um intervalo de datas:
--     - quantidade de viagens,
--     - custo total,
--     - tempo médio de deslocamento em minutos.
--
-- Operadores/recursos usados:
--   - Filtro por CPF e intervalo de datas
--   - Funções de agregação: COUNT, SUM, AVG
--   - Função de data/tempo: EXTRACT(EPOCH FROM ...)
--   - Cálculo do tempo médio em minutos
------------------------------------------------------------

SELECT
    COUNT(*) AS quantidade_viagens,
    COALESCE(SUM(CUSTO_TOTAL), 0) AS custo_total,
    AVG(EXTRACT(EPOCH FROM (DATAHORA_FINAL - DATAHORA_INICIO)) / 60.0)
        AS tempo_medio_minutos
FROM VIAGEM
WHERE CPF_CIDADAO = '11111111111'            -- trocar pelo CPF desejado
  AND DATAHORA_INICIO >= DATE '2025-11-01'   -- data inicial do período
  AND DATAHORA_INICIO <  DATE '2025-12-01';  -- data final (exclusivo)


------------------------------------------------------------
-- 3) Linhas mais usadas por um cidadão
--
-- Objetivo:
--   Identificar quais linhas um cidadão mais utiliza, ordenando
--   da linha com maior número de viagens para a menor.
--
-- Operadores/recursos usados:
--   - Filtro por CPF
--   - GROUP BY na linha de embarque
--   - COUNT(*) para contar viagens
--   - ORDER BY para ordenar por quantidade de viagens (ranking)
------------------------------------------------------------

SELECT
    v.NOME_CODIGO_LINHA_EMBARQUE AS linha,
    COUNT(*)                     AS qtd_viagens
FROM VIAGEM v
WHERE v.CPF_CIDADAO = '11111111111'   -- trocar pelo CPF desejado
GROUP BY v.NOME_CODIGO_LINHA_EMBARQUE
ORDER BY qtd_viagens DESC, linha;


------------------------------------------------------------
-- 4) Rotas mais utilizadas entre bairros
--
-- Objetivo:
--   Descobrir quais trajetos entre bairros de origem e destino
--   são mais frequentes no sistema, considerando os pontos de
--   embarque e desembarque das viagens.
--
-- Operadores/recursos usados:
--   - JOIN duplo com PONTO_PARADA (embarque e desembarque)
--   - GROUP BY em par (bairro_origem, bairro_destino)
--   - COUNT(*) para quantificar viagens por par de bairros
--   - ORDER BY quantidade de viagens (trajetos mais populares)
------------------------------------------------------------

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


------------------------------------------------------------
-- 5) Cidadãos que usaram TODAS as linhas de uma empresa pública
--
-- Objetivo:
--   Listar os cidadãos que já realizaram ao menos uma viagem em
--   TODAS as linhas operadas por uma determinada empresa pública.
--
-- Esta consulta é um exemplo de DIVISÃO RELACIONAL:
--   - Conjunto "dividendo": viagens (VIAGEM) de cada cidadão.
--   - Conjunto "divisor": linhas da empresa (LINHA filtrada por CNPJ).
--   - Resultado: cidadãos cujo conjunto de linhas utilizadas contém
--     todas as linhas da empresa.
--
-- Implementação em SQL:
--   - Uso de NOT EXISTS aninhado:
--       "não existe linha da empresa tal que não exista uma viagem
--        do cidadão nessa linha".
--   - Envolve subconsultas correlacionadas entre USUARIO_CIDADAO,
--     LINHA e VIAGEM.
------------------------------------------------------------

SELECT
    uc.CPF,
    uc.EMAIL
FROM USUARIO_CIDADAO uc
WHERE NOT EXISTS (
    -- Verifica se existe alguma linha da empresa que este cidadão NÃO usou
    SELECT 1
    FROM LINHA l
    WHERE l.CNPJ_EMPRESA_PUBLICA = '66666666000106'   -- CNPJ da empresa
      AND NOT EXISTS (
          SELECT 1
          FROM VIAGEM v
          WHERE v.CPF_CIDADAO = uc.CPF
            AND v.NOME_CODIGO_LINHA_EMBARQUE = l.NOME_CODIGO
      )
);
