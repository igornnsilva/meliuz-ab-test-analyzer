from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.formatters import (
    format_currency_brl,
    format_integer_brl,
)


PAGE_WIDTH, _ = landscape(A4)


def format_percentage(value: float) -> str:
    """Formata uma proporção como porcentagem."""
    if pd.isna(value):
        return "N/A"

    return f"{float(value) * 100:.2f}%".replace(".", ",")


def format_decimal(
    value: float,
    decimal_places: int = 2,
) -> str:
    """Formata um número decimal usando vírgula."""
    if pd.isna(value):
        return "N/A"

    return (
        f"{float(value):.{decimal_places}f}"
        .replace(".", ",")
    )


def build_styles() -> dict[str, ParagraphStyle]:
    """Cria os estilos tipográficos utilizados no PDF."""
    base_styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "PdfTitle",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#202124"),
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "PdfSubtitle",
            parent=base_styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5F6368"),
            spaceAfter=16,
        ),
        "heading": ParagraphStyle(
            "PdfHeading",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=colors.HexColor("#202124"),
            spaceBefore=8,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "PdfBody",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#202124"),
            spaceAfter=6,
        ),
        "table_header": ParagraphStyle(
            "PdfTableHeader",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#202124"),
        ),
        "table_cell": ParagraphStyle(
            "PdfTableCell",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#202124"),
        ),
        "decision_title": ParagraphStyle(
            "PdfDecisionTitle",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#202124"),
            spaceAfter=6,
        ),
        "decision_body": ParagraphStyle(
            "PdfDecisionBody",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#202124"),
        ),
    }


def safe_paragraph(
    value: object,
    style: ParagraphStyle,
) -> Paragraph:
    """Cria um parágrafo seguro para o ReportLab."""
    return Paragraph(
        escape(str(value)),
        style,
    )


def add_page_footer(canvas, document) -> None:
    """Adiciona rodapé e numeração em todas as páginas."""
    canvas.saveState()

    canvas.setStrokeColor(
        colors.HexColor("#DADCE0")
    )
    canvas.setLineWidth(0.5)

    canvas.line(
        1.2 * cm,
        1.15 * cm,
        PAGE_WIDTH - 1.2 * cm,
        1.15 * cm,
    )

    canvas.setFont(
        "Helvetica",
        7.5,
    )

    canvas.setFillColor(
        colors.HexColor("#5F6368")
    )

    canvas.drawString(
        1.2 * cm,
        0.72 * cm,
        (
            "Relatório gerado automaticamente pelo "
            "analisador de testes A/B."
        ),
    )

    canvas.drawRightString(
        PAGE_WIDTH - 1.2 * cm,
        0.72 * cm,
        f"Página {document.page}",
    )

    canvas.restoreState()


def build_metadata_table(
    analyzed_df: pd.DataFrame,
    quality: dict,
    decision: dict,
    styles: dict[str, ParagraphStyle],
) -> Table:
    """Monta o bloco de identificação do experimento."""
    start_date = analyzed_df["Data"].min().strftime(
        "%d/%m/%Y"
    )

    end_date = analyzed_df["Data"].max().strftime(
        "%d/%m/%Y"
    )

    data = [
        [
            safe_paragraph(
                "Parceiro",
                styles["table_header"],
            ),
            safe_paragraph(
                "Período",
                styles["table_header"],
            ),
            safe_paragraph(
                "Status dos dados",
                styles["table_header"],
            ),
            safe_paragraph(
                "Grupo de controle",
                styles["table_header"],
            ),
        ],
        [
            safe_paragraph(
                decision["parceiro"],
                styles["table_cell"],
            ),
            safe_paragraph(
                f"{start_date} até {end_date}",
                styles["table_cell"],
            ),
            safe_paragraph(
                quality["status"],
                styles["table_cell"],
            ),
            safe_paragraph(
                decision["grupo_controle"],
                styles["table_cell"],
            ),
        ],
    ]

    table = Table(
        data,
        colWidths=[
            5.5 * cm,
            6.0 * cm,
            6.5 * cm,
            6.5 * cm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#F1F3F4"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DADCE0"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    return table


def build_decision_box(
    decision: dict,
    styles: dict[str, ParagraphStyle],
) -> Table:
    """Monta o bloco de destaque da decisão recomendada."""
    is_success = bool(
        decision["escalar_automaticamente"]
    )

    background_color = colors.HexColor(
        "#E6F4EA"
        if is_success
        else "#FEF7E0"
    )

    border_color = colors.HexColor(
        "#188038"
        if is_success
        else "#F9AB00"
    )

    content = [
        Paragraph(
            "Decisão recomendada",
            styles["decision_title"],
        ),
        Paragraph(
            (
                "<b>Decisão:</b> "
                f"{escape(str(decision['decisao']))}"
            ),
            styles["decision_body"],
        ),
        Paragraph(
            (
                "<b>Grupo recomendado:</b> "
                f"{escape(str(decision['grupo_recomendado']))}"
            ),
            styles["decision_body"],
        ),
        Paragraph(
            (
                "<b>Confiança:</b> "
                f"{escape(str(decision['confianca']))}"
            ),
            styles["decision_body"],
        ),
        Spacer(
            1,
            4,
        ),
        Paragraph(
            (
                "<b>Justificativa:</b><br/>"
                f"{escape(str(decision['motivo']))}"
            ),
            styles["decision_body"],
        ),
    ]

    table = Table(
        [[content]],
        colWidths=[24.5 * cm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    background_color,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1.5,
                    border_color,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    return table


def build_quality_section(
    quality: dict,
    styles: dict[str, ParagraphStyle],
) -> list:
    """Monta a seção de qualidade dos dados."""
    warnings = quality.get(
        "avisos",
        [],
    )

    elements = [
        Paragraph(
            "Qualidade dos dados",
            styles["heading"],
        )
    ]

    if warnings:
        for warning in warnings:
            elements.append(
                Paragraph(
                    (
                        "• "
                        f"{escape(str(warning))}"
                    ),
                    styles["body"],
                )
            )
    else:
        elements.append(
            Paragraph(
                (
                    "Nenhum problema relevante "
                    "foi encontrado."
                ),
                styles["body"],
            )
        )

    return elements


def build_summary_table(
    summary: pd.DataFrame,
    styles: dict[str, ParagraphStyle],
) -> LongTable:
    """Monta a tabela consolidada por grupo."""
    headers = [
        "Variante",
        "Dias",
        "Compradores",
        "Vendas totais",
        "Cashback",
        "Receita líquida",
        "Ticket médio",
        "Taxa cashback",
        "Margem líquida",
    ]

    data = [
        [
            safe_paragraph(
                header,
                styles["table_header"],
            )
            for header in headers
        ]
    ]

    for _, row in summary.iterrows():
        values = [
            row["Grupos de usuários"],
            int(row["dias"]),
            format_integer_brl(
                row["compradores"]
            ),
            format_currency_brl(
                row["vendas_totais"]
            ),
            format_currency_brl(
                row["cashback"]
            ),
            format_currency_brl(
                row["receita_liquida"]
            ),
            format_currency_brl(
                row["ticket_medio"]
            ),
            format_percentage(
                row["taxa_cashback"]
            ),
            format_percentage(
                row["margem_liquida"]
            ),
        ]

        data.append(
            [
                safe_paragraph(
                    value,
                    styles["table_cell"],
                )
                for value in values
            ]
        )

    table = LongTable(
        data,
        repeatRows=1,
        colWidths=[
            2.6 * cm,
            1.2 * cm,
            2.0 * cm,
            2.7 * cm,
            2.4 * cm,
            2.7 * cm,
            2.4 * cm,
            2.2 * cm,
            2.2 * cm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#F1F3F4"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    colors.HexColor("#DADCE0"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#FAFAFA"),
                    ],
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    return table


def build_statistical_table(
    comparisons: pd.DataFrame,
    styles: dict[str, ParagraphStyle],
) -> LongTable:
    """Monta a tabela das comparações estatísticas."""
    metric_names = {
        "compradores": "Compradores",
        "vendas totais": "Vendas totais",
        "receita_liquida": "Receita líquida",
        "ticket_medio": "Ticket médio",
    }

    main_metrics = list(
        metric_names.keys()
    )

    filtered_comparisons = comparisons.loc[
        comparisons["metrica"].isin(
            main_metrics
        )
    ].copy()

    headers = [
        "Variante",
        "Métrica",
        "Lift",
        "P-valor",
        "IC 95%",
        "Significativo",
    ]

    data = [
        [
            safe_paragraph(
                header,
                styles["table_header"],
            )
            for header in headers
        ]
    ]

    for _, row in filtered_comparisons.iterrows():
        lift = (
            "N/A"
            if pd.isna(
                row["lift_percentual"]
            )
            else (
                f"{float(row['lift_percentual']):+.2f}%"
                .replace(".", ",")
            )
        )

        p_value = format_decimal(
            row["p_valor_t_pareado"],
            decimal_places=6,
        )

        if (
            pd.isna(row["ic95_inferior"])
            or pd.isna(row["ic95_superior"])
        ):
            confidence_interval = "N/A"
        else:
            confidence_interval = (
                "["
                f"{format_decimal(row['ic95_inferior'])}; "
                f"{format_decimal(row['ic95_superior'])}"
                "]"
            )

        significant = (
            "Sim"
            if bool(row["significativo_5pct"])
            else "Não"
        )

        values = [
            row["grupo_variante"],
            metric_names.get(
                row["metrica"],
                row["metrica"],
            ),
            lift,
            p_value,
            confidence_interval,
            significant,
        ]

        data.append(
            [
                safe_paragraph(
                    value,
                    styles["table_cell"],
                )
                for value in values
            ]
        )

    table_styles = [
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#F1F3F4"),
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.35,
            colors.HexColor("#DADCE0"),
        ),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [
                colors.white,
                colors.HexColor("#FAFAFA"),
            ],
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE",
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            5,
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            5,
        ),
    ]

    if filtered_comparisons.empty:
        data.append(
            [
                safe_paragraph(
                    (
                        "Nenhuma comparação "
                        "estatística disponível."
                    ),
                    styles["table_cell"],
                ),
                "",
                "",
                "",
                "",
                "",
            ]
        )

        table_styles.append(
            (
                "SPAN",
                (0, 1),
                (-1, 1),
            )
        )

    table = LongTable(
        data,
        repeatRows=1,
        colWidths=[
            3.2 * cm,
            4.0 * cm,
            2.2 * cm,
            2.4 * cm,
            5.0 * cm,
            3.0 * cm,
        ],
    )

    table.setStyle(
        TableStyle(
            table_styles
        )
    )

    return table


def create_scaled_image(
    image_path: Path,
    max_width: float,
    max_height: float,
) -> Image:
    """Redimensiona uma imagem preservando a proporção."""
    image = Image(
        str(image_path)
    )

    scale = min(
        max_width / image.imageWidth,
        max_height / image.imageHeight,
        1.0,
    )

    image.drawWidth = (
        image.imageWidth * scale
    )

    image.drawHeight = (
        image.imageHeight * scale
    )

    return image


def build_chart_pages(
    chart_paths: dict[str, Path],
    styles: dict[str, ParagraphStyle],
) -> list:
    """Monta as páginas contendo os gráficos."""
    chart_titles = {
        "vendas": "Vendas totais por dia",
        "compradores": "Compradores por dia",
        "receita": "Receita líquida por dia",
        "cashback": (
            "Estabilidade da taxa de cashback"
        ),
        "receita_total": (
            "Receita líquida total"
        ),
    }

    elements = [
        PageBreak(),
        Paragraph(
            "Visualizações",
            styles["heading"],
        ),
    ]

    valid_charts = [
        (
            chart_name,
            Path(chart_path),
        )
        for chart_name, chart_path
        in chart_paths.items()
        if Path(chart_path).exists()
    ]

    if not valid_charts:
        elements.append(
            Paragraph(
                (
                    "Nenhum gráfico foi encontrado "
                    "para inclusão no PDF."
                ),
                styles["body"],
            )
        )

        return elements

    for index, (
        chart_name,
        chart_path,
    ) in enumerate(valid_charts):
        chart_title = chart_titles.get(
            chart_name,
            chart_name.replace(
                "_",
                " ",
            ).title(),
        )

        chart_block = [
            Paragraph(
                escape(chart_title),
                styles["heading"],
            ),
            Spacer(
                1,
                4,
            ),
            create_scaled_image(
                image_path=chart_path,
                max_width=23.5 * cm,
                max_height=13.5 * cm,
            ),
            Spacer(
                1,
                10,
            ),
        ]

        elements.append(
            KeepTogether(
                chart_block
            )
        )

        if index < len(valid_charts) - 1:
            elements.append(
                PageBreak()
            )

    return elements


def generate_pdf_report(
    analyzed_df: pd.DataFrame,
    summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    quality: dict,
    decision: dict,
    chart_paths: dict[str, Path],
    report_directory: Path,
) -> Path:
    """
    Gera um relatório PDF completo e apresentável.
    """
    report_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        report_directory
        / "relatorio.pdf"
    )

    styles = build_styles()

    document = SimpleDocTemplate(
        str(report_path),
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.55 * cm,
        title=(
            "Relatório A/B - "
            f"{decision['parceiro']}"
        ),
        author=(
            "Analisador de testes A/B"
        ),
        subject=(
            "Análise de experimento de cashback"
        ),
    )

    story = [
        Paragraph(
            "Relatório de Teste A/B de Cashback",
            styles["title"],
        ),
        Paragraph(
            (
                "Resumo executivo, qualidade dos dados, "
                "resultados consolidados e "
                "evidências estatísticas."
            ),
            styles["subtitle"],
        ),
        build_metadata_table(
            analyzed_df=analyzed_df,
            quality=quality,
            decision=decision,
            styles=styles,
        ),
        Spacer(
            1,
            12,
        ),
        build_decision_box(
            decision=decision,
            styles=styles,
        ),
        Spacer(
            1,
            10,
        ),
    ]

    story.extend(
        build_quality_section(
            quality=quality,
            styles=styles,
        )
    )

    story.extend(
        [
            Spacer(
                1,
                6,
            ),
            Paragraph(
                "Resultados consolidados",
                styles["heading"],
            ),
            build_summary_table(
                summary=summary,
                styles=styles,
            ),
            Spacer(
                1,
                12,
            ),
            Paragraph(
                "Comparações estatísticas",
                styles["heading"],
            ),
            Paragraph(
                (
                    "As variantes foram comparadas com o "
                    "grupo de controle utilizando "
                    "observações pareadas por data."
                ),
                styles["body"],
            ),
            build_statistical_table(
                comparisons=comparisons,
                styles=styles,
            ),
        ]
    )

    story.extend(
        build_chart_pages(
            chart_paths=chart_paths,
            styles=styles,
        )
    )

    document.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )

    return report_path

