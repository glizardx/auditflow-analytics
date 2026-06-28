WITH operational_volume AS (
    SELECT
        IDREGISTROCONTROLADO AS tipo,
        COUNT(*) AS total_fluxos
    FROM fluxos
    GROUP BY IDREGISTROCONTROLADO
),

quality_summary AS (
    SELECT
        TIPO_DE_AUTORIZACAO AS tipo,
        COUNT(*) AS total_inspecoes,
        SUM(
            CASE
                WHEN GRAVIDADE <> 'SEM_ERRO' THEN 1
                ELSE 0
            END
        ) AS total_erros,
        AVG(
            CASE
                WHEN GRAVIDADE <> 'SEM_ERRO' THEN 1
                ELSE 0
            END
        ) * 100 AS taxa_erro
    FROM inspecoes
    GROUP BY TIPO_DE_AUTORIZACAO
)

SELECT
    COALESCE(operational_volume.tipo, quality_summary.tipo) AS tipo,
    COALESCE(total_fluxos, 0) AS total_fluxos,
    COALESCE(total_inspecoes, 0) AS total_inspecoes,
    COALESCE(total_erros, 0) AS total_erros,
    ROUND(COALESCE(taxa_erro, 0), 2) AS taxa_erro,
    ROUND(COALESCE(total_fluxos, 0) * COALESCE(taxa_erro, 0) / 100, 2) AS score_prioridade
FROM operational_volume
FULL OUTER JOIN quality_summary
    ON operational_volume.tipo = quality_summary.tipo
ORDER BY score_prioridade DESC;
