from django.db import models


ICON_CHOICES = [
  ("award", "Award"),
  ("bar-chart-3", "Bar Chart"),
  ("briefcase", "Briefcase"),
  ("camera", "Camera"),
  ("code-2", "Code"),
  ("cpu", "CPU"),
  ("globe", "Globe"),
]

SOCIAL_PLATFORM_CHOICES = [
  ("github", "GitHub"),
  ("linkedin", "LinkedIn"),
  ("instagram", "Instagram"),
  ("x", "X"),
  ("facebook", "Facebook"),
  ("youtube", "YouTube"),
  ("behance", "Behance"),
  ("dribbble", "Dribbble"),
  ("globe", "Website"),
]


class OrderedModel(models.Model):
  position = models.PositiveIntegerField(default=0)

  class Meta:
    abstract = True
    ordering = ["position", "id"]


class PortfolioPage(models.Model):
  name = models.CharField(max_length=200)
  headline = models.CharField(max_length=255)
  hero_badge = models.CharField(max_length=255)
  hero_description = models.TextField()
  about_eyebrow = models.CharField(max_length=80, default="About")
  about_title = models.CharField(max_length=200, default="Professional Profile")
  skills_eyebrow = models.CharField(max_length=80, default="Skills")
  skills_title = models.CharField(max_length=200, default="Technical Capabilities")
  projects_eyebrow = models.CharField(max_length=80, default="Projects")
  projects_title = models.CharField(max_length=200, default="Selected Work")
  experience_title = models.CharField(max_length=200, default="Experience")
  education_title = models.CharField(max_length=200, default="Education")
  certifications_title = models.CharField(max_length=200, default="Certifications")
  contact_eyebrow = models.CharField(max_length=80, default="Contact")
  about_text = models.TextField()
  contact_title = models.CharField(max_length=255)
  contact_description = models.TextField()
  location = models.CharField(max_length=150)
  email = models.EmailField()
  phone = models.CharField(max_length=50)
  github_label = models.CharField(max_length=120, blank=True)
  github_url = models.URLField(blank=True)
  linkedin_label = models.CharField(max_length=120, blank=True, default="")
  linkedin_url = models.URLField(blank=True, default="")
  cv_filename = models.CharField(max_length=200, default="Achiek_Deng_CV.pdf")
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = "Portfolio Page"
    verbose_name_plural = "Portfolio Page"

  def __str__(self):
    return self.name

  @property
  def email_href(self):
    return f"mailto:{self.email}"

  @property
  def phone_href(self):
    normalized = "".join(char for char in self.phone if char.isdigit() or char == "+")
    return f"tel:{normalized}"


class FocusArea(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="focus_areas", on_delete=models.CASCADE)
  label = models.CharField(max_length=120)

  def __str__(self):
    return self.label


class Metric(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="metrics", on_delete=models.CASCADE)
  value = models.CharField(max_length=40)
  label = models.CharField(max_length=160)

  def __str__(self):
    return f"{self.value} - {self.label}"


class Strength(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="strengths", on_delete=models.CASCADE)
  title = models.CharField(max_length=160)
  description = models.TextField()

  def __str__(self):
    return self.title


class SkillCategory(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="skills", on_delete=models.CASCADE)
  title = models.CharField(max_length=160)
  icon = models.CharField(max_length=40, choices=ICON_CHOICES)
  summary = models.TextField(blank=True)

  class Meta(OrderedModel.Meta):
    verbose_name_plural = "Skill categories"

  def __str__(self):
    return self.title


class SkillEntry(OrderedModel):
  skill = models.ForeignKey(SkillCategory, related_name="entries", on_delete=models.CASCADE)
  label = models.CharField(max_length=120)

  def __str__(self):
    return self.label


class Project(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="projects", on_delete=models.CASCADE)
  title = models.CharField(max_length=200)
  category = models.CharField(max_length=160, blank=True)
  period = models.CharField(max_length=80)
  icon = models.CharField(max_length=40, choices=ICON_CHOICES)
  url = models.URLField(blank=True, default="")
  description = models.TextField()

  def __str__(self):
    return self.title


class ProjectStackItem(OrderedModel):
  project = models.ForeignKey(Project, related_name="stack_items", on_delete=models.CASCADE)
  label = models.CharField(max_length=120)

  def __str__(self):
    return self.label


class ProjectHighlight(OrderedModel):
  project = models.ForeignKey(Project, related_name="highlights", on_delete=models.CASCADE)
  text = models.CharField(max_length=255)

  def __str__(self):
    return self.text


class ExperienceItem(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="experience_items", on_delete=models.CASCADE)
  role = models.CharField(max_length=200)
  organization = models.CharField(max_length=200, blank=True)
  period = models.CharField(max_length=80)
  description = models.TextField()

  def __str__(self):
    return self.role


class EducationItem(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="education_items", on_delete=models.CASCADE)
  title = models.CharField(max_length=200)
  organization = models.CharField(max_length=200)
  period = models.CharField(max_length=80)

  def __str__(self):
    return self.title


class CertificationItem(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="certification_items", on_delete=models.CASCADE)
  title = models.CharField(max_length=200)

  def __str__(self):
    return self.title


class SocialLink(OrderedModel):
  page = models.ForeignKey(PortfolioPage, related_name="social_links", on_delete=models.CASCADE)
  platform = models.CharField(max_length=40, choices=SOCIAL_PLATFORM_CHOICES, default="globe")
  label = models.CharField(max_length=120, blank=True)
  url = models.URLField()

  class Meta(OrderedModel.Meta):
    verbose_name = "Social link"
    verbose_name_plural = "Social links"

  def __str__(self):
    return self.label or self.get_platform_display()
