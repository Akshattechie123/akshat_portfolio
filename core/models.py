from django.db import models

STATUS = [("new", "New"), ("reviewed", "Reviewed"), ("closed", "Closed")]

class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS, default="new")
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"{self.name} - {self.subject or 'Message'}"

class ProjectBrief(models.Model):
    TYPES = [("Website", "Website"), ("Management System", "Management System"), ("Dashboard", "Dashboard"),
             ("API / Backend", "API / Backend"), ("E-commerce", "E-commerce"), ("Other", "Other")]
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=200, blank=True)
    project_type = models.CharField(max_length=40, choices=TYPES, blank=True)
    goal = models.TextField(blank=True)
    target_users = models.CharField(max_length=300, blank=True)
    features = models.TextField(blank=True)
    reference_links = models.TextField(blank=True)
    budget = models.CharField(max_length=60, blank=True)
    timeline = models.CharField(max_length=60, blank=True)
    constraints = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="new")
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"{self.full_name} - {self.title or self.project_type}"

class ProjectFile(models.Model):
    brief = models.ForeignKey(ProjectBrief, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="briefs/%Y/%m/")
    def __str__(self): return self.file.name

class WebsiteProject(models.Model):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    tech_tags = models.CharField(max_length=200, blank=True, help_text="Comma separated")
    image = models.ImageField(upload_to="websites/", blank=True)
    live_link = models.URLField(blank=True)
    github_link = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["order", "-id"]
    def tags(self): return [t.strip() for t in self.tech_tags.split(",") if t.strip()]
    def __str__(self): return self.title

class BackendProject(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    tech_tags = models.CharField(max_length=200, blank=True, help_text="Comma separated")
    image = models.ImageField(upload_to="backend/", blank=True)
    github_link = models.URLField(blank=True)
    pdf = models.FileField(upload_to="backend/pdf/", blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["order", "-id"]
    def tags(self): return [t.strip() for t in self.tech_tags.split(",") if t.strip()]
    def __str__(self): return self.title
