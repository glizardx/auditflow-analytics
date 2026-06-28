# Checklist para Publicar no GitHub

Antes de publicar este projeto, confira:

- [ ] Os arquivos reais em `data/raw/` nao foram adicionados ao Git.
- [ ] O projeto publico usa `python src/run_sample_pipeline.py`.
- [ ] Os CSVs tratados em `data/processed/` nao foram adicionados ao Git.
- [ ] O banco em `data/database/` nao foi adicionado ao Git.
- [ ] Prints do dashboard nao exibem dados sensiveis.
- [ ] O README explica que os dados foram anonimizados.
- [ ] O README explica que a versao publica usa dados sinteticos.
- [ ] O arquivo `docs/data_dictionary.md` esta atualizado.
- [ ] O dashboard roda com `streamlit run app/streamlit_app.py`.
- [ ] O pipeline sintetico roda com `python src/run_sample_pipeline.py`.

## Comandos Uteis

Verificar arquivos que entrariam no Git:

```bash
git status
```

Verificar se existem nomes ou documentos sensiveis em arquivos publicados:

```bash
grep -R "termo_sensivel" README.md docs src sql app
```

## Observacao

Para portfolio publico, o ideal e publicar uma amostra ficticia ou sintetica, nao os dados reais.
