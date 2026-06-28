# Dicionário de Dados

Este documento descreve as principais tabelas tratadas do projeto.

## Tabela `inspecoes`

Origem: `data/processed/inspecoes_limpas.csv`

Representa registros de inspeções de qualidade.

| Coluna | Descrição |
| --- | --- |
| `COORDENACAO` | Código anonimizado da coordenação. |
| `LIDERANCA` | Código anonimizado da liderança. |
| `DATA_DA_INSPECAO` | Data em que a inspeção foi realizada. |
| `INSPETOR` | Código anonimizado do inspetor. |
| `CPF_CNPJ` | Código anonimizado do documento. |
| `COOP` | Código anonimizado da cooperativa/unidade. |
| `TIPO` | Tipo geral do registro. |
| `DATA_DE_EXECUCAO` | Data de execução do processo inspecionado. |
| `INTERNO_OU_EXTERNO` | Origem do processo. |
| `TIPO_DE_AUTORIZACAO` | Categoria generalizada do processo inspecionado, como `processo_abc123def0`. |
| `COLABORADOR` | Código anonimizado do colaborador. |
| `TIPO_DE_ERRO` | Tipo de erro identificado. |
| `GRAVIDADE` | Gravidade do erro: `SEM_ERRO`, `GRAVE` ou `GRAVISSIMO`. |
| `DESVIO_DE_ATENCAO` | Indica se houve desvio de atenção. |
| `REVERSAO` | Indica se houve reversão. |
| `TEM_DESCRICAO` | Indica se a linha tinha descrição textual no dado bruto. |

## Tabela `fluxos`

Origem: `data/processed/fluxos_limpos.csv`

Representa registros operacionais de fluxo/processo.

| Coluna | Descrição |
| --- | --- |
| `IDPROCESSO` | Identificador do processo. |
| `NOMEPROCESSO` | Codigo anonimizado do nome/categoria do processo. |
| `IDOCORRENCIAPROCESSO` | Identificador da ocorrência do processo. |
| `IDREGISTROCONTROLADO` | Tipo de processo generalizado, como `processo_abc123def0`. |
| `USUARIO` | Código anonimizado do usuário. |
| `ATIVIDADE` | Atividade executada no fluxo. |
| `PROCEDIMENTO` | Procedimento realizado. |
| `SITUACAOFLUXO` | Situação do fluxo, como `COMPLETO` ou `INICIADO`. |
| `DATAHORAINICIOATIVIDADE` | Data e hora de início da atividade. |
| `DATAHORAFIMATIVIDADE` | Data e hora de fim da atividade. |
| `DURACAO_MINUTOS` | Duração calculada da atividade em minutos. |
| `TEM_JUSTIFICATIVA` | Indica se a linha tinha justificativa textual no dado bruto. |

## Observações de Privacidade

Campos sensíveis foram substituídos por hashes estáveis. Isso permite agrupar e contar registros sem revelar nomes, documentos ou estruturas reais.
