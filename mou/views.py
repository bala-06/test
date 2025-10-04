from django.shortcuts import render, redirect, get_object_or_404
from .models import MOU, Event
from .forms import MOUForm
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q
from datetime import date
from .models import MOU, Department, Outcome
from django.db.models import Prefetch
from .forms import EventForm
from .forms import MOUFilterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import LoginAttempt
from django.views.decorators.http import require_POST
from django.middleware import csrf
from django.contrib.auth.models import User
import io
from django.http import HttpResponse
import matplotlib
# Use Agg backend to avoid GUI/Tk dependencies
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import urllib.request
from datetime import datetime
def mou_report_pdf(request, mou_id):
    """Generate a nicely formatted PDF report using ReportLab Platypus.

    Includes a large logo, MOU details table, pie chart image, and two tables
    listing completed and pending events with details.
    """
    mou = get_object_or_404(MOU.objects.prefetch_related('department', 'outcome'), id=mou_id)
    events = list(mou.events.all())

    # Count statuses
    completed_events = [e for e in events if getattr(e, 'status', '').lower() == 'completed']
    pending_events = [e for e in events if getattr(e, 'status', '').lower() != 'completed']

    completed = len(completed_events)
    pending = len(pending_events)

    # Create pie chart in memory
    fig, ax = plt.subplots(figsize=(4, 3))
    sizes = [completed, pending]
    labels = [f'Completed ({completed})', f'Pending ({pending})']
    colors = ['#28a745', '#ffc107']
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
    ax.axis('equal')

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')
    plt.close(fig)
    img_buf.seek(0)

    # Build PDF with Platypus (improved layout)
    pdf_buf = io.BytesIO()
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.pagesizes import letter

    doc = SimpleDocTemplate(pdf_buf, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=16, leading=20))
    styles.add(ParagraphStyle(name='Small', fontSize=9))
    normal = styles['Normal']
    small = styles['Small']

    story = []

    # Big logo
    logo_url = 'https://www.bitsathy.ac.in/wp-content/themes/baiotsathycollege/assets/images/header%2006.png'
    try:
        with urllib.request.urlopen(logo_url, timeout=5) as resp:
            logo_data = resp.read()
            logo_image = RLImage(io.BytesIO(logo_data), width=3.5*inch, height=1.2*inch)
            story.append(logo_image)
    except Exception:
        pass

    story.append(Spacer(1, 8))
    story.append(Paragraph('Bannari Amman Institute of Technology', styles['CenterTitle']))
    story.append(Spacer(1, 12))

    # Left: MOU details table (use Paragraphs for wrapping)
    def p(text):
        return Paragraph(text or '-', normal)

    mou_details = [
        [p('<b>MOU Title:</b>'), p(mou.title)],
        [p('<b>Organization:</b>'), p(mou.organization_name or '-')],
        [p('<b>Departments:</b>'), p(', '.join(d.name for d in mou.department.all()))],
        [p('<b>Start Date:</b>'), p(str(mou.start_date))],
        [p('<b>End Date:</b>'), p(str(mou.end_date))],
        [p('<b>Status:</b>'), p(mou.status)],
        [p('<b>MOU Coordinator:</b>'), p(f"{mou.mou_coordinator_name or '-'} ({mou.mou_coordinator_mobile or '-'})")],
        [p('<b>MOU Coordinator Email:</b>'), p(mou.mou_coordinator_email or '-')],
        [p('<b>Staff Coordinator:</b>'), p(f"{mou.staff_coordinator_name or '-'} ({mou.staff_coordinator_mobile or '-'})")],
        [p('<b>Staff Coordinator Email:</b>'), p(mou.staff_coordinator_email or '-')],
        [p('<b>Outcomes:</b>'), p(', '.join(o.name for o in mou.outcome.all()))],
        [p('<b>Payment Amount:</b>'), p(f'₹{mou.payment_paid}')],
    ]

    details_table = Table(mou_details, colWidths=[140, 340])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))

    # Right: chart and totals
    chart_img = RLImage(img_buf, width=4*inch, height=3*inch)
    totals_para = Paragraph(f'<b>Total events:</b> {len(events)} &nbsp;&nbsp; <b>Completed:</b> {completed} &nbsp;&nbsp; <b>Pending:</b> {pending}', normal)
    right_frame = [chart_img, Spacer(1,6), totals_para]

    # Two-column top table: details | chart+totals
    top_table = Table([[details_table, right_frame]], colWidths=[3.2*inch, 3.2*inch])
    top_table.setStyle(TableStyle([('VALIGN', (0,0),(1,0),'TOP')]))
    story.append(top_table)
    story.append(Spacer(1, 12))

    # Completed events
    story.append(Paragraph('<b>Completed Events</b>', styles['Heading3']))
    if completed_events:
        comp_rows = [[p('<b>Title</b>'), p('<b>Date</b>'), p('<b>Description</b>')]]
        for ev in completed_events:
            desc = (ev.description or '').replace('\n', ' ')
            if len(desc) > 500:
                desc = desc[:497] + '...'
            comp_rows.append([p(ev.title), p(str(ev.date)), p(desc)])
        comp_table = Table(comp_rows, colWidths=[2.6*inch, 1.2*inch, 2.2*inch])
        comp_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(comp_table)
    else:
        story.append(Paragraph('No completed events.', normal))

    story.append(Spacer(1,12))

    # Pending events
    story.append(Paragraph('<b>Pending Events</b>', styles['Heading3']))
    if pending_events:
        pend_rows = [[p('<b>Title</b>'), p('<b>Date</b>'), p('<b>Description</b>')]]
        for ev in pending_events:
            desc = (ev.description or '').replace('\n', ' ')
            if len(desc) > 500:
                desc = desc[:497] + '...'
            pend_rows.append([p(ev.title), p(str(ev.date)), p(desc)])
        pend_table = Table(pend_rows, colWidths=[2.6*inch, 1.2*inch, 2.2*inch])
        pend_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fafafa')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(pend_table)
    else:
        story.append(Paragraph('No pending events.', normal))

    # Build and return
    doc.build(story)
    pdf_buf.seek(0)
    return HttpResponse(pdf_buf.getvalue(), content_type='application/pdf')

def add_event(request, mou_id):
    mou = get_object_or_404(MOU, id=mou_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.mou = mou
            event.save()
            messages.success(request, 'Event added successfully!')
            return redirect('view_mou', mou_id=mou.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm()
    
    return render(request, 'mou/add_event.html', {
        'form': form,
        'mou': mou
    })

def filter_mou(request):
    form = MOUFilterForm(request.GET or None)
    mous = MOU.objects.all()

    # Apply filters
    if form.is_valid():
        if form.cleaned_data['title']:
            mous = mous.filter(title__icontains=form.cleaned_data['title'])
        if form.cleaned_data['organization_name']:
            mous = mous.filter(organization_name__icontains=form.cleaned_data['organization_name'])
        if form.cleaned_data['department']:
            mous = mous.filter(department=form.cleaned_data['department'])
        if form.cleaned_data['outcome']:
            mous = mous.filter(outcome=form.cleaned_data['outcome'])
        if form.cleaned_data['status']:
            mous = mous.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['start_date']:
            mous = mous.filter(start_date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            mous = mous.filter(end_date__lte=form.cleaned_data['end_date'])

    return render(request, 'mou/filter_mou.html', {'form': form, 'mous': mous})
def group_mous_by_department(mous):
    departments = Department.objects.filter(mous__in=mous).distinct()
    grouped = []
    for department in departments:
        grouped.append({
            'department_name': department.name,
            'mous': mous.filter(department=department),
        })
    return grouped

def mou_list(request):
    today = date.today()
    active_mous = MOU.objects.filter(end_date__gte=today).prefetch_related('department', 'outcome')
    expired_mous = MOU.objects.filter(end_date__lt=today).prefetch_related('department', 'outcome')

    active_mous_by_department = group_mous_by_department(active_mous)
    expired_mous_by_department = group_mous_by_department(expired_mous)

    return render(request, 'mou/mou_list.html', {
        'active_mous_by_department': active_mous_by_department,
        'expired_mous_by_department': expired_mous_by_department,
    })
def create_mou(request):
    if request.method == 'POST':
        form = MOUForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('mou_list')
    else:
        form = MOUForm()
    return render(request, 'mou/create_mou.html', {'form': form})


def view_mou(request, mou_id):
    mou = get_object_or_404(MOU.objects.prefetch_related('department', 'outcome'), id=mou_id)
    events = mou.events.all()
    department = ', '.join([dept.name for dept in mou.department.all()])
    outcome = ', '.join([out.name for out in mou.outcome.all()])

    return render(request, 'mou/view_mou.html', {
        'mou': mou,
        'events': events,
        'department': department,
        'outcome': outcome,
    })

def edit_mou(request, mou_id):
    mou = get_object_or_404(MOU, id=mou_id)
    if request.method == 'POST':
        form = MOUForm(request.POST, request.FILES, instance=mou)
        if form.is_valid():
            form.save()
            return redirect('mou_list')
    else:
        form = MOUForm(instance=mou)
    return render(request, 'mou/edit_mou.html', {'form': form, 'mou': mou})


@login_required
def edit_mou(request, mou_id):
    mou = get_object_or_404(MOU, id=mou_id)
    if request.method == 'POST':
        form = MOUForm(request.POST, request.FILES, instance=mou)
        if form.is_valid():
            form.save()
            return redirect('mou_list')
    else:
        form = MOUForm(instance=mou)
    return render(request, 'mou/edit_mou.html', {'form': form, 'mou': mou})

def delete_mou(request, mou_id):
    mou = get_object_or_404(MOU, id=mou_id)
    mou.delete()
    return redirect('mou_list')


@login_required
def delete_mou(request, mou_id):
    mou = get_object_or_404(MOU, id=mou_id)
    mou.delete()
    return redirect('mou_list')

def edit_event(request, event_id):
    print(f"Edit Event View Called for Event ID: {event_id}")
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        print("POST request received.")
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            
            print("Form is valid. Saving changes...")
            form.save()
            print("Event saved. Redirecting to view_event.")
            id=event_id
            mou_id = event.mou.id
            return redirect('view_mou', mou_id=mou_id)
        else:
            print("Form is not valid:", form.errors)
    else:
        form = EventForm(instance=event)
    return render(request, 'mou/edit_event.html', {'form': form, 'event': event})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            mou_id = event.mou.id
            return redirect('view_mou', mou_id=mou_id)
    else:
        form = EventForm(instance=event)
    return render(request, 'mou/edit_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    mou_id = event.mou.id
    event.delete()
    return redirect('view_mou', mou_id=mou_id)


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    mou_id = event.mou.id
    event.delete()
    return redirect('view_mou', mou_id=mou_id)

def about(request):
    return render(request, 'mou/about.html')

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Event, Department, Outcome, MOU

def show_database(request):
    # Fetch all records from the database
    records = Event.objects.all()
    records1 = Department.objects.all()
    records2 = Outcome.objects.all()
    records3 = MOU.objects.all()

    # Add pagination for event records
    paginator = Paginator(records, 10)  # Show 10 records per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)

    return render(request, 'mou/show_database.html', {
        'records': page_obj,
        'records1': records1,
        'records2': records2,
        'records3': records3
    })


@login_required
def show_database(request):
    # Fetch all records from the database
    records = Event.objects.all()
    records1 = Department.objects.all()
    records2 = Outcome.objects.all()
    records3 = MOU.objects.all()

    # Add pagination for event records
    paginator = Paginator(records, 10)  # Show 10 records per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)

    return render(request, 'mou/show_database.html', {
        'records': page_obj,
        'records1': records1,
        'records2': records2,
        'records3': records3
    })

def student(request):
    today = date.today()
    active_mous = MOU.objects.filter(end_date__gte=today).prefetch_related('department', 'outcome')
    expired_mous = MOU.objects.filter(end_date__lt=today).prefetch_related('department', 'outcome')

    active_mous_by_department = group_mous_by_department(active_mous)
    expired_mous_by_department = group_mous_by_department(expired_mous)

    return render(request, 'mou/student.html', {
        'active_mous_by_department': active_mous_by_department,
        'expired_mous_by_department': expired_mous_by_department,
    })

def company(request):
    today = date.today()
    active_mous = MOU.objects.filter(end_date__gte=today).prefetch_related('department', 'outcome')
    expired_mous = MOU.objects.filter(end_date__lt=today).prefetch_related('department', 'outcome')

    active_mous_by_department = group_mous_by_department(active_mous)
    expired_mous_by_department = group_mous_by_department(expired_mous)

    return render(request, 'mou/company.html', {
        'active_mous_by_department': active_mous_by_department,
        'expired_mous_by_department': expired_mous_by_department,
    })

def student_view(request,mou_id):
    mou = get_object_or_404(MOU.objects.prefetch_related('department', 'outcome'), id=mou_id)
    events = mou.events.all()
    department = ', '.join([dept.name for dept in mou.department.all()])
    outcome = ', '.join([out.name for out in mou.outcome.all()])

    return render(request, 'mou/studentview.html', {
        'mou': mou,
        'events': events,
        'department': department,
        'outcome': outcome,
    })


def login_view(request):
    """Display and process login form. Students can still access student pages without login."""
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        username = request.POST.get('username')
        ip = request.META.get('REMOTE_ADDR')
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # record successful attempt
            try:
                LoginAttempt.objects.create(username=username or '', success=True, ip_address=ip)
            except Exception:
                pass
            messages.success(request, 'Logged in successfully.')
            if next_url:
                return redirect(next_url)
            return redirect('mou_list')
        else:
            # record failed attempt
            try:
                LoginAttempt.objects.create(username=username or '', success=False, ip_address=ip)
            except Exception:
                pass
            messages.error(request, 'Login failed. Check your credentials and try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'mou/login.html', {'form': form, 'next': next_url})


@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('mou_list')


def register(request):
    """Simple user registration view used by the register.html template."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'mou/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'mou/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully. You can now login.')
        return redirect('login')

    return render(request, 'mou/register.html')