from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.timezone import localtime
from datetime import datetime
import openpyxl
from reportlab.pdfgen import canvas

from .models import Price, Entry

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Entry



def dashboard(request):
    price = Price.objects.last()

    # -----------------------------
    # HANDLE PRICE UPDATE
    # -----------------------------
    if request.method == "POST" and 'price_per_liter' in request.POST:
        value = float(request.POST.get('price_per_liter'))

        if price:
            price.price_per_liter = value
            price.save()
        else:
            Price.objects.create(price_per_liter=value)

        return redirect('dashboard')

    # -----------------------------
    # HANDLE ENTRY ADD
    # -----------------------------
    if request.method == "POST" and 'liter' in request.POST:
        if not price:
            return redirect('dashboard')

        liter = float(request.POST['liter'])
        amount = liter * price.price_per_liter

        Entry.objects.create(
            liter=liter,
            price_per_liter=price.price_per_liter,
            amount=amount
        )
        return redirect('dashboard')

    # -----------------------------
    # DATE FILTER (USING created_at)
    # -----------------------------
    selected_date = request.GET.get('date')

    if selected_date:
        entries = Entry.objects.filter(
            created_at__date=selected_date
        ).order_by('-created_at')
    else:
        entries = Entry.objects.all().order_by('-created_at')

    total_liter = sum(e.liter for e in entries)
    total_amount = sum(e.amount for e in entries)

    return render(request, 'dashboard.html', {
        'price': price,
        'entries': entries,
        'total_liter': total_liter,
        'total_amount': total_amount,
        'selected_date': selected_date
    })


# =====================================================
# MONTHLY REPORT (HTML)
# =====================================================
def monthly_report(request):
    month = request.GET.get('month')  # YYYY-MM

    entries = []
    total_liter = 0
    total_amount = 0

    if month:
        year, mon = month.split('-')
        entries = Entry.objects.filter(
            created_at__year=year,
            created_at__month=mon
        ).order_by('created_at')

        total_liter = sum(e.liter for e in entries)
        total_amount = sum(e.amount for e in entries)

    return render(request, 'monthly_report.html', {
        'entries': entries,
        'total_liter': total_liter,
        'total_amount': total_amount,
        'month': month
    })


# =====================================================
# MONTHLY EXCEL DOWNLOAD
# =====================================================
def monthly_excel(request):
    month = request.GET.get('month')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Monthly Report"

    ws.append(["Date", "Time", "Liter", "Price/L", "Amount"])

    total = 0

    if month:
        year, mon = month.split('-')
        entries = Entry.objects.filter(
            created_at__year=year,
            created_at__month=mon
        ).order_by('created_at')
    else:
        entries = Entry.objects.all().order_by('created_at')

    for e in entries:
        dt = localtime(e.created_at)
        ws.append([
            dt.strftime("%d-%m-%Y"),
            dt.strftime("%I:%M %p"),
            e.liter,
            e.price_per_liter,
            e.amount
        ])
        total += e.amount

    ws.append([])
    ws.append(["", "", "", "Total", total])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=monthly_report.xlsx'
    wb.save(response)

    return response


# =====================================================
# PDF DOWNLOAD
# =====================================================
def download_pdf(request):
    entries = Entry.objects.all().order_by('created_at')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="milk_report.pdf"'

    p = canvas.Canvas(response)
    y = 800
    total = 0

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Milk Entry Report")
    y -= 40

    p.setFont("Helvetica", 10)

    for e in entries:
        dt = localtime(e.created_at)
        line = f"{dt.strftime('%d %b %Y %I:%M %p')} | {e.liter} L | ₹{e.amount}"
        p.drawString(50, y, line)
        total += e.amount
        y -= 20

        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = 800

    y -= 20
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, f"Total Amount: ₹ {total}")

    p.showPage()
    p.save()
    return response


# =====================================================
# DELETE ENTRY
# =====================================================
def delete_entry(request, entry_id):
    Entry.objects.filter(id=entry_id).delete()
    return redirect('dashboard')


# =====================================================
# EDIT ENTRY
# =====================================================
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    price = Price.objects.last()

    if request.method == "POST":
        liter = float(request.POST['liter'])
        new_price = float(request.POST['price_per_liter'])

        # Update global price
        if price:
            price.price_per_liter = new_price
            price.save()
        else:
            price = Price.objects.create(price_per_liter=new_price)

        # Update entry
        entry.liter = liter
        entry.price_per_liter = new_price
        entry.amount = liter * new_price
        entry.save()

        return redirect('dashboard')

    return render(request, 'edit_entry.html', {
        'entry': entry,
        'price': price
    })


@api_view(['GET'])
def entry_list(request):
    data = list(Entry.objects.values())
    return Response(data)