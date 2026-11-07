import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


class HondaPDFGenerator:

    def __init__(self, output_dir="quotations"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, quotation, filename=None):

        if filename is None:
            filename = "Vision_Honda_Quotation_" + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            ) + ".pdf"

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        path = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=12*mm,
            bottomMargin=15*mm
        )

        styles = getSampleStyleSheet()

        title = ParagraphStyle(
            "HondaTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=27,
            textColor=colors.HexColor("#12385A"),
            alignment=TA_CENTER,
            spaceAfter=4
        )

        subtitle = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=TA_CENTER
        )

        normal = ParagraphStyle(
            "HondaNormal",
            parent=styles["Normal"],
            fontSize=9,
            leading=13
        )

        banner_style = ParagraphStyle(
            "BookingBanner",
            parent=normal,
            fontSize=9,
            leading=13,
            textColor=colors.white,
            alignment=TA_CENTER
        )

        story = []

        # Priority Booking Banner
        banner = Paragraph(
            "<b>PRIORITY BOOKING — BOOK YOUR HONDA AT ₹5,000*</b>"
            "<br/>100% REFUNDABLE BOOKING AMOUNT"
            "<br/>Book early for booking assistance and updates "
            "on vehicle availability and allocation.",
            banner_style
        )

        banner_table = Table(
            [[banner]],
            colWidths=[180*mm]
        )

        banner_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1),
             colors.HexColor("#12385A")),
            ("BOX", (0,0), (-1,-1), 1,
             colors.HexColor("#12385A")),
            ("TOPPADDING", (0,0), (-1,-1), 9),
            ("BOTTOMPADDING", (0,0), (-1,-1), 9),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ]))

        story.append(banner_table)
        story.append(Spacer(1, 10*mm))

        story.append(Paragraph(
            "<b>VISION HONDA</b>", title
        ))

        story.append(Paragraph(
            "Customer Price Quotation",
            subtitle
        ))

        story.append(Spacer(1, 8*mm))

        # Customer Details
        customer_data = [
            ["Customer Name", quotation.get("customer", "")],
            ["Mobile Number", quotation.get("mobile", "")],
            ["Model", quotation.get("model", "")],
            ["Variant", quotation.get("variant", "")],
            ["Colour", quotation.get("colour", "")],
            ["Quotation Date", datetime.now().strftime("%d-%m-%Y")]
        ]

        customer_table = Table(
            customer_data,
            colWidths=[48*mm, 132*mm]
        )

        customer_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1),
             colors.HexColor("#EAF0F6")),
            ("TEXTCOLOR", (0,0), (0,-1),
             colors.HexColor("#12385A")),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5,
             colors.HexColor("#B7C5D3")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ]))

        story.append(customer_table)
        story.append(Spacer(1, 8*mm))

        # Price Table
        story.append(Paragraph(
            "<b>ON-ROAD PRICE BREAKUP</b>",
            normal
        ))

        story.append(Spacer(1, 3*mm))

        items = quotation.get("items", {})

        rows = [["Description", "Amount (INR)"]]

        order = [
            "Ex-showroom",
            "TCS",
            "Insurance",
            "Zero Depreciation",
            "Road Tax",
            "Registration + Fastag",
            "Accessories",
            "RSA"
        ]

        for name in order:
            amount = float(items.get(name, 0))
            rows.append([
                name,
                "₹{:,.2f}".format(amount)
            ])

        total = float(quotation.get("subtotal", 0))
        discount = float(quotation.get("discount", 0))
        payable = float(quotation.get("payable", total))

        rows.append([
            "TOTAL ON-ROAD (BEFORE DISCOUNT)",
            "₹{:,.2f}".format(total)
        ])

        if discount > 0:
            rows.append([
                "Discount",
                "- ₹{:,.2f}".format(discount)
            ])

        rows.append([
            "FINAL PAYABLE AMOUNT",
            "₹{:,.2f}".format(payable)
        ])

        price_table = Table(
            rows,
            colWidths=[125*mm, 55*mm],
            repeatRows=1
        )

        price_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0),
             colors.HexColor("#12385A")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
            ("GRID", (0,0), (-1,-1), 0.5,
             colors.HexColor("#C5CED8")),
            ("BACKGROUND", (0,-1), (-1,-1),
             colors.HexColor("#DCEAF5")),
            ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0,-1), (-1,-1),
             colors.HexColor("#12385A")),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ]))

        story.append(price_table)
        story.append(Spacer(1, 10*mm))

        story.append(Paragraph(
            "<b>Booking Terms & Conditions</b>",
            normal
        ))

        story.append(Paragraph(
            "Booking amount starts at ₹5,000 and is 100% refundable. "
            "Vehicle availability, allocation, prices and applicable "
            "dealership terms are subject to confirmation.",
            normal
        ))

        story.append(Spacer(1, 12*mm))

        signature = Table([
            ["Customer Signature", "Sales Consultant"]
        ], colWidths=[90*mm, 90*mm])

        signature.setStyle(TableStyle([
            ("LINEABOVE", (0,0), (-1,-1), 0.5,
             colors.grey),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("FONTSIZE", (0,0), (-1,-1), 9),
        ]))

        story.append(signature)

        doc.build(story)

        return path