import io
from datetime import UTC, datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFReportGenerator:
    """
    Deterministic, production-grade PDF Kundli Report Generator.
    Produces comprehensive Vedic charts, planetary tables, classical yogas, and citations.
    """

    @classmethod
    def generate_chart_report(
        cls,
        profile_data: dict[str, Any],
        chart_calc_data: dict[str, Any],
        rules_data: dict[str, Any] | None = None,
        transits_data: dict[str, Any] | None = None,
        report_id: str | None = None,
    ) -> bytes:
        """
        Generates a professional PDF report and returns the raw PDF bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b"),
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
        )
        h2_style = ParagraphStyle(
            "Heading2Style",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        disclaimer_style = ParagraphStyle(
            "DisclaimerStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#78350f"),
        )

        story = []

        # 1. HEADER & BANNER
        story.append(Paragraph("AstroMind AI — Vedic Kundli Report", title_style))
        gen_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        rep_id = report_id or "REP-AUTO"
        story.append(
            Paragraph(
                f"Generated on: {gen_time} &bull; Report ID: <code>{rep_id}</code> &bull; Astronomical Engine: Swiss Ephemeris",
                subtitle_style,
            )
        )
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#d97706"), spaceAfter=12))

        # 2. NATIVE DETAILS SUMMARY TABLE
        story.append(Paragraph("1. Native Birth & Ephemeris Details", h2_style))
        meta = chart_calc_data.get("metadata", {})
        birth_summary = [
            ["Native Name:", profile_data.get("name", "N/A"), "Birth Date & Time:", f"{profile_data.get('birth_date')} {profile_data.get('birth_time') or 'Approximate'}"],
            ["Birth Place:", profile_data.get("birthplace", "N/A"), "Timezone:", profile_data.get("timezone", "N/A")],
            ["Coordinates:", f"Lat: {profile_data.get('latitude')}, Lon: {profile_data.get('longitude')}", "Ayanamsa:", f"{meta.get('ayanamsa', 'lahiri').title()} ({meta.get('ayanamsa_value', 24.0):.4f}°)"],
            ["Ascendant (Lagna):", f"{chart_calc_data.get('ascendant_sign_name', 'N/A')} ({chart_calc_data.get('ascendant_degree', 0.0):.2f}°)", "House System:", "Whole-Sign (Classical Parashari)"],
        ]
        t_birth = Table(birth_summary, colWidths=[1.4 * inch, 2.3 * inch, 1.4 * inch, 2.4 * inch])
        t_birth.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
            ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#475569")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_birth)
        story.append(Spacer(1, 10))

        # 3. PLANETARY POSITIONS TABLE
        story.append(Paragraph("2. Sidereal Planetary Longitudes & Nakshatras", h2_style))
        planets_data = [["Planet", "Sign", "Degree in Sign", "Nakshatra", "Pada", "House", "Motion"]]
        for p in chart_calc_data.get("planets", []):
            retro = "Retrograde" if p.get("is_retrograde") else "Direct"
            planets_data.append([
                p.get("planet_id", ""),
                p.get("sign_name", ""),
                f"{p.get('degree_in_sign', 0.0):.2f}°",
                p.get("nakshatra_name", ""),
                str(p.get("pada", 1)),
                f"House {p.get('house_number', 1)}",
                retro,
            ])
        t_planets = Table(planets_data, colWidths=[1.1 * inch, 1.1 * inch, 1.1 * inch, 1.4 * inch, 0.7 * inch, 1.0 * inch, 1.1 * inch])
        t_planets.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_planets)
        story.append(Spacer(1, 10))

        # 4. CLASSICAL YOGAS & DIGNITIES SECTION
        if rules_data:
            story.append(Paragraph("3. Classical Vedic Yogas & Interpretive Rules", h2_style))
            yogas = rules_data.get("yogas", [])
            if yogas:
                for y in yogas[:6]:  # Include top identified yogas
                    story.append(Paragraph(f"<b>&bull; {y.get('name')} ({y.get('category')} Yoga):</b> {y.get('description')} <i>[Ref: {y.get('classical_reference')}]</i>", body_style))
                    story.append(Spacer(1, 3))
            else:
                story.append(Paragraph("No major classical Raja or Dhana yogas detected in this configuration.", body_style))
            story.append(Spacer(1, 6))

        # 5. GOCHAR TRANSITS & SADE SATI
        if transits_data:
            story.append(Paragraph("4. Current Gochar Transits & Sade Sati Analysis", h2_style))
            ss = transits_data.get("sade_sati", {})
            ss_text = f"<b>Sade Sati Status:</b> {'ACTIVE — ' + ss.get('phase', '') if ss.get('is_active') else 'NOT ACTIVE'}. {ss.get('description', '')}"
            story.append(Paragraph(ss_text, body_style))
            story.append(Spacer(1, 4))
            highlights = transits_data.get("summary_highlights", [])
            if highlights:
                for hl in highlights:
                    story.append(Paragraph(f"&bull; {hl}", body_style))
            story.append(Spacer(1, 6))

        # 6. VIMSHOTTARI DASHA TIMELINE
        story.append(Paragraph("5. Vimshottari Dasha Major Periods (Mahadashas)", h2_style))
        dasha_rows = [["Dasha Lord", "Start Date", "End Date", "Duration"]]
        for d in chart_calc_data.get("vimshottari_dashas", [])[:9]:
            dasha_rows.append([
                d.get("lord", ""),
                d.get("start_date", "")[:10],
                d.get("end_date", "")[:10],
                f"{d.get('duration_years', 0):.1f} Years",
            ])
        t_dasha = Table(dasha_rows, colWidths=[1.8 * inch, 1.9 * inch, 1.9 * inch, 1.9 * inch])
        t_dasha.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t_dasha)
        story.append(Spacer(1, 14))

        # 7. MANDATORY ETHICAL DISCLAIMER
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
        disclaimer_p = (
            "<b>ETHICAL & PROFESSIONAL ADVISORY NOTICE:</b> Vedic astrology is a traditional cultural and philosophical "
            "discipline intended for introspection, archetypal reflection, and personal study. Planetary calculations "
            "do not claim to predict unalterable future events or destiny. Under no circumstances should this analysis "
            "be interpreted as medical, financial, psychiatric, or legal advice."
        )
        story.append(Paragraph(disclaimer_p, disclaimer_style))

        doc.build(story)
        return buffer.getvalue()
