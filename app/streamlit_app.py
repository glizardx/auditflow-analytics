import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


DATABASE_PATH = "data/database/auditflow.duckdb"


@st.cache_data
def run_query(query: str) -> pd.DataFrame:
    connection = duckdb.connect(DATABASE_PATH, read_only=True)
    result = connection.execute(query).fetchdf()
    connection.close()
    return result


def add_multiselect_filter(label: str, dataframe: pd.DataFrame, column: str) -> list[str]:
    values = sorted(dataframe[column].dropna().unique())
    return st.sidebar.multiselect(label, values)


def apply_filter(dataframe: pd.DataFrame, column: str, selected_values: list[str]) -> pd.DataFrame:
    if not selected_values:
        return dataframe

    return dataframe[dataframe[column].isin(selected_values)]


st.set_page_config(
    page_title="AuditFlow Analytics",
    layout="wide",
)

st.title("AuditFlow Analytics")

inspecoes = run_query(
    """
    SELECT *
    FROM inspecoes;
    """
)

fluxos = run_query(
    """
    SELECT *
    FROM fluxos;
    """
)

st.sidebar.header("Filtros")
selected_coordenacao = add_multiselect_filter("Coordenacao", inspecoes, "COORDENACAO")
selected_lideranca = add_multiselect_filter("Lideranca", inspecoes, "LIDERANCA")
selected_tipo = add_multiselect_filter("Tipo de autorizacao", inspecoes, "TIPO_DE_AUTORIZACAO")
selected_gravidade = add_multiselect_filter("Gravidade", inspecoes, "GRAVIDADE")

filtered = inspecoes.copy()
filtered = apply_filter(filtered, "COORDENACAO", selected_coordenacao)
filtered = apply_filter(filtered, "LIDERANCA", selected_lideranca)
filtered = apply_filter(filtered, "TIPO_DE_AUTORIZACAO", selected_tipo)
filtered = apply_filter(filtered, "GRAVIDADE", selected_gravidade)

filtered["TEM_ERRO"] = filtered["GRAVIDADE"] != "SEM_ERRO"

total_inspecoes = len(filtered)
total_erros = int(filtered["TEM_ERRO"].sum())
taxa_erro = total_erros / total_inspecoes * 100 if total_inspecoes else 0

by_type = (
    filtered.groupby("TIPO_DE_AUTORIZACAO", dropna=False)
    .agg(
        total_inspecoes=("TEM_ERRO", "count"),
        total_erros=("TEM_ERRO", "sum"),
        taxa_erro=("TEM_ERRO", "mean"),
    )
    .reset_index()
)
by_type["taxa_erro"] = by_type["taxa_erro"] * 100
by_type = by_type.sort_values("taxa_erro", ascending=False)

by_severity = (
    filtered.groupby("GRAVIDADE", dropna=False)
    .size()
    .reset_index(name="total")
    .sort_values("total", ascending=False)
)

by_leadership = (
    filtered.groupby("LIDERANCA", dropna=False)
    .agg(
        total_inspecoes=("TEM_ERRO", "count"),
        total_erros=("TEM_ERRO", "sum"),
        taxa_erro=("TEM_ERRO", "mean"),
    )
    .reset_index()
)
by_leadership["taxa_erro"] = by_leadership["taxa_erro"] * 100
by_leadership = by_leadership.sort_values("taxa_erro", ascending=False)

tab_quality, tab_operations, tab_comparison = st.tabs(
    ["Qualidade", "Fluxos operacionais", "Comparativo"]
)

with tab_quality:
    col1, col2, col3 = st.columns(3)
    col1.metric("Inspecoes", f"{total_inspecoes:,}".replace(",", "."))
    col2.metric("Erros", f"{total_erros:,}".replace(",", "."))
    col3.metric("Taxa de erro", f"{taxa_erro:.2f}%")

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Taxa de erro por tipo de autorizacao")
        if by_type.empty:
            st.info("Nenhum dado encontrado para os filtros selecionados.")
        else:
            fig_rate = px.bar(
                by_type,
                x="taxa_erro",
                y="TIPO_DE_AUTORIZACAO",
                orientation="h",
                text="taxa_erro",
                labels={
                    "taxa_erro": "Taxa de erro (%)",
                    "TIPO_DE_AUTORIZACAO": "Tipo de autorizacao",
                },
            )
            fig_rate.update_layout(yaxis={"categoryorder": "total ascending"})
            fig_rate.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            st.plotly_chart(fig_rate, use_container_width=True)

    with right:
        st.subheader("Inspecoes por gravidade")
        if by_severity.empty:
            st.info("Nenhum dado encontrado para os filtros selecionados.")
        else:
            fig_severity = px.bar(
                by_severity,
                x="GRAVIDADE",
                y="total",
                text="total",
                labels={
                    "GRAVIDADE": "Gravidade",
                    "total": "Total",
                },
            )
            fig_severity.update_traces(textposition="outside")
            st.plotly_chart(fig_severity, use_container_width=True)

    st.subheader("Resumo por tipo de autorizacao")
    st.dataframe(
        by_type.round(2),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Impacto absoluto vs risco proporcional")
    if by_type.empty:
        st.info("Nenhum dado encontrado para os filtros selecionados.")
    else:
        fig_impact = px.scatter(
            by_type,
            x="total_inspecoes",
            y="taxa_erro",
            size="total_erros",
            color="TIPO_DE_AUTORIZACAO",
            hover_data=["total_erros"],
            labels={
                "total_inspecoes": "Total de inspecoes",
                "taxa_erro": "Taxa de erro (%)",
                "total_erros": "Total de erros",
                "TIPO_DE_AUTORIZACAO": "Tipo de autorizacao",
            },
        )
        st.plotly_chart(fig_impact, use_container_width=True)

    st.subheader("Ranking por lideranca")
    st.dataframe(
        by_leadership.round(2),
        use_container_width=True,
        hide_index=True,
    )

with tab_operations:
    fluxos["DATAHORAINICIOATIVIDADE"] = pd.to_datetime(
        fluxos["DATAHORAINICIOATIVIDADE"],
        errors="coerce",
    )
    fluxos_validos = fluxos[fluxos["DURACAO_MINUTOS"].notna()].copy()
    fluxos_validos = fluxos_validos[fluxos_validos["DURACAO_MINUTOS"] >= 0]

    total_fluxos = len(fluxos)
    fluxos_completos = int((fluxos["SITUACAOFLUXO"] == "COMPLETO").sum())
    taxa_completos = fluxos_completos / total_fluxos * 100 if total_fluxos else 0
    mediana_duracao = fluxos_validos["DURACAO_MINUTOS"].median()

    col1, col2, col3 = st.columns(3)
    col1.metric("Fluxos", f"{total_fluxos:,}".replace(",", "."))
    col2.metric("Fluxos completos", f"{taxa_completos:.2f}%")
    col3.metric("Mediana de duracao", f"{mediana_duracao:.1f} min")

    by_process = (
        fluxos.groupby("IDREGISTROCONTROLADO", dropna=False)
        .agg(
            total_fluxos=("IDPROCESSO", "count"),
            duracao_mediana=("DURACAO_MINUTOS", "median"),
            duracao_media=("DURACAO_MINUTOS", "mean"),
        )
        .reset_index()
        .sort_values("total_fluxos", ascending=False)
    )

    by_status = (
        fluxos.groupby("SITUACAOFLUXO", dropna=False)
        .size()
        .reset_index(name="total")
        .sort_values("total", ascending=False)
    )

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Volume por tipo de processo")
        fig_process = px.bar(
            by_process,
            x="total_fluxos",
            y="IDREGISTROCONTROLADO",
            orientation="h",
            text="total_fluxos",
            labels={
                "total_fluxos": "Total de fluxos",
                "IDREGISTROCONTROLADO": "Tipo de processo",
            },
        )
        fig_process.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_process.update_traces(textposition="outside")
        st.plotly_chart(fig_process, use_container_width=True)

    with right:
        st.subheader("Fluxos por situacao")
        fig_status = px.bar(
            by_status,
            x="SITUACAOFLUXO",
            y="total",
            text="total",
            labels={
                "SITUACAOFLUXO": "Situacao",
                "total": "Total",
            },
        )
        fig_status.update_traces(textposition="outside")
        st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("Resumo operacional por tipo de processo")
    st.dataframe(
        by_process.round(2),
        use_container_width=True,
        hide_index=True,
    )

with tab_comparison:
    st.subheader("Volume operacional vs qualidade")

    operational_volume = (
        fluxos.groupby("IDREGISTROCONTROLADO", dropna=False)
        .size()
        .reset_index(name="total_fluxos")
        .rename(columns={"IDREGISTROCONTROLADO": "tipo"})
    )

    quality_summary = (
        inspecoes.groupby("TIPO_DE_AUTORIZACAO", dropna=False)
        .agg(
            total_inspecoes=("TIPO_DE_AUTORIZACAO", "count"),
            total_erros=(
                "GRAVIDADE",
                lambda values: (values != "SEM_ERRO").sum(),
            ),
        )
        .reset_index()
        .rename(columns={"TIPO_DE_AUTORIZACAO": "tipo"})
    )
    quality_summary["taxa_erro"] = (
        quality_summary["total_erros"] / quality_summary["total_inspecoes"] * 100
    )

    comparison = operational_volume.merge(
        quality_summary,
        on="tipo",
        how="outer",
    ).fillna(0)

    comparison["score_prioridade"] = (
        comparison["total_fluxos"] * comparison["taxa_erro"] / 100
    )
    comparison = comparison.sort_values("score_prioridade", ascending=False)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        fig_comparison = px.scatter(
            comparison,
            x="total_fluxos",
            y="taxa_erro",
            size="total_erros",
            color="tipo",
            hover_data=[
                "total_inspecoes",
                "total_erros",
                "score_prioridade",
            ],
            labels={
                "total_fluxos": "Volume operacional",
                "taxa_erro": "Taxa de erro (%)",
                "total_erros": "Total de erros",
                "tipo": "Tipo",
            },
        )
        st.plotly_chart(fig_comparison, use_container_width=True)

    with col2:
        top_priority = comparison.head(5)[
            [
                "tipo",
                "total_fluxos",
                "total_erros",
                "taxa_erro",
                "score_prioridade",
            ]
        ]
        st.dataframe(
            top_priority.round(2),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Tabela comparativa completa")
    st.dataframe(
        comparison.round(2),
        use_container_width=True,
        hide_index=True,
    )
