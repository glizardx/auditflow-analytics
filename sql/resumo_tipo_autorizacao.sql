SELECT
    TIPO_DE_AUTORIZACAO,
    COUNT(*) AS total_inspecoes,
    SUM(
        CASE
            WHEN GRAVIDADE <> 'SEM_ERRO' THEN 1
            ELSE 0
        END
    ) AS total_erros,
    ROUND(
        AVG(
            CASE
                WHEN GRAVIDADE <> 'SEM_ERRO' THEN 1
                ELSE 0
            END
        ) * 100,
        2
    ) AS taxa_erro
FROM inspecoes
GROUP BY TIPO_DE_AUTORIZACAO
ORDER BY taxa_erro DESC;
