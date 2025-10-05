from django.db import models




class Event(models.Model):
    mou = models.ForeignKey('MOU', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
        ],
        default='Pending'
    )

    def __str__(self):
        return f"{self.title} ({self.status})"
class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Outcome(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class MOU(models.Model):
    # MOU Title
    title = models.CharField(max_length=255)
    organization_name = models.CharField(max_length=255, blank=True, null=True)


    # Department (Multiple selection with full forms)
    department_choices = [
        ('cse', 'Computer Science and Engineering'),
        ('it', 'Information Technology'),
        ('ece', 'Electronics and Communication Engineering'),
        ('mech', 'Mechanical Engineering'),
        ('civil', 'Civil Engineering'),
    ]
    department = models.ManyToManyField('Department', related_name='mous')
    # Date range of MOU
    start_date = models.DateField()
    end_date = models.DateField()

    # Optional document upload
    document = models.FileField(upload_to='mou_documents/', blank=True, null=True)

    # MOU Status
    status_choices = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='draft')

    # MOU Coordinator Details
    mou_coordinator_name = models.CharField(max_length=100, blank=True, null=True)
    mou_coordinator_mobile = models.CharField(max_length=15, blank=True, null=True)
    mou_coordinator_email = models.EmailField(blank=True, null=True)

    # Staff Coordinator Details
    staff_coordinator_name = models.CharField(max_length=100, blank=True, null=True)
    staff_coordinator_mobile = models.CharField(max_length=15, blank=True, null=True)
    staff_coordinator_email = models.EmailField(blank=True, null=True)

    # Outcome of MOU (Multiple selection)
    outcome_choices = [
        ('placement', 'Placement'),
        ('iv', 'Industrial Visit'),
        ('workshop', 'Workshop'),
        ('research', 'Research Collaboration'),
        ('internship', 'Internship'),
    ]
    outcome = models.ManyToManyField(Outcome, related_name='mous')

    # Payment amount (Numeric input instead of boolean)
    # Payment amount
    payment_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.title


class LoginAttempt(models.Model):
    """
    Simple model to keep track of login attempts. Not required for auth but useful for auditing.
    """
    username = models.CharField(max_length=150)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {'success' if self.success else 'failure'} @ {self.timestamp}"


class OrgOTP(models.Model):
    """One-time passcodes for organization email login."""
    email = models.EmailField()
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.email} ({'used' if self.used else 'active'})"
