from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

def generate_invoice_pdf(order):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"<b>INVOICE #{order.id}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Order Info
    order_info = f"""
    <b>Order Date:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}<br/>
    <b>Customer:</b> {order.customer.get_full_name() or order.customer.username}<br/>
    <b>Email:</b> {order.customer.email}<br/>
    <b>Phone:</b> {order.phone}<br/>
    <b>Shipping Address:</b> {order.shipping_address}<br/>
    <b>Status:</b> {order.get_status_display()}
    """
    elements.append(Paragraph(order_info, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Order Items Table
    data = [['Product', 'Quantity', 'Price', 'Subtotal']]
    
    for item in order.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"${item.price:.2f}",
            f"${item.subtotal:.2f}"
        ])
    
    # Add total
    data.append(['', '', '<b>Total:</b>', f"<b>${order.total_amount:.2f}</b>"])
    
    table = Table(data, colWidths=[3*inch, 1*inch, 1*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer = Paragraph("Thank you for your purchase!", styles['Normal'])
    elements.append(footer)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf