import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from subscriptions.models import Subscription, Category
from analytics_app.utils import (
    get_monthly_spending_data,
    get_category_breakdown,
    get_yearly_projection,
)


@login_required
def overview(request):
    """Reports overview page."""
    user = request.user
    
    # Get data
    monthly_data = get_monthly_spending_data(user, months=12)
    category_data = get_category_breakdown(user)
    projection = get_yearly_projection(user)
    
    # Subscription stats
    active_subs = Subscription.objects.filter(user=user, status='active')
    total_subscriptions = active_subs.count()
    monthly_spend = sum(s.monthly_cost for s in active_subs)
    yearly_spend = monthly_spend * 12
    
    context = {
        'monthly_data': monthly_data,
        'category_data': category_data,
        'projection': projection,
        'total_subscriptions': total_subscriptions,
        'monthly_spend': monthly_spend,
        'yearly_spend': yearly_spend,
    }
    return render(request, 'reports/overview.html', context)


@login_required
def export_csv(request):
    """Export subscriptions to CSV."""
    user = request.user
    subscriptions = Subscription.objects.filter(user=user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="subtrack_report_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Category', 'Description', 'Price', 'Currency',
        'Billing Cycle', 'Monthly Cost', 'Yearly Cost',
        'Renewal Date', 'Status', 'Payment Method',
        'Website', 'Notes', 'Auto Detected', 'Created At',
    ])
    
    for sub in subscriptions:
        writer.writerow([
            sub.name,
            sub.category.name if sub.category else 'Uncategorized',
            sub.description,
            sub.price,
            sub.currency,
            sub.get_billing_cycle_display(),
            f"{sub.monthly_cost:.2f}",
            f"{sub.yearly_cost:.2f}",
            sub.renewal_date,
            sub.get_status_display(),
            sub.get_payment_method_display(),
            sub.website_url,
            sub.notes,
            'Yes' if sub.is_auto_detected else 'No',
            sub.created_at.strftime('%Y-%m-%d'),
        ])
    
    return response


@login_required
def export_pdf(request):
    """Export report to PDF."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    
    user = request.user
    subscriptions = Subscription.objects.filter(user=user)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=30,
    )
    
    # Title
    elements.append(Paragraph(f"SubTrack Report - {user.full_name}", title_style))
    elements.append(Paragraph(f"Generated on {timezone.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Summary
    active_subs = subscriptions.filter(status='active')
    monthly_spend = sum(s.monthly_cost for s in active_subs)
    
    summary_data = [
        ['Total Subscriptions', str(subscriptions.count())],
        ['Active Subscriptions', str(active_subs.count())],
        ['Monthly Spend', f"{user.currency_symbol}{monthly_spend:,.2f}"],
        ['Yearly Projection', f"{user.currency_symbol}{monthly_spend * 12:,.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Subscriptions table
    elements.append(Paragraph("Subscription Details", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    table_data = [['Name', 'Category', 'Price', 'Cycle', 'Status', 'Renewal']]
    for sub in subscriptions:
        table_data.append([
            sub.name,
            sub.category.name if sub.category else '-',
            f"{sub.currency_symbol}{sub.price}",
            sub.get_billing_cycle_display(),
            sub.get_status_display(),
            sub.renewal_date.strftime('%Y-%m-%d') if sub.renewal_date else '-',
        ])
    
    if len(table_data) > 1:
        sub_table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        sub_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ]))
        elements.append(sub_table)
    else:
        elements.append(Paragraph("No subscriptions found.", styles['Normal']))
    
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="subtrack_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response
