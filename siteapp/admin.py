from django.contrib import admin

from .models import (
  CertificationItem,
  EducationItem,
  ExperienceItem,
  FocusArea,
  Metric,
  PortfolioPage,
  Project,
  ProjectHighlight,
  ProjectStackItem,
  SocialLink,
  SkillCategory,
  SkillEntry,
  Strength,
)


class FocusAreaInline(admin.TabularInline):
  model = FocusArea
  extra = 0


class MetricInline(admin.TabularInline):
  model = Metric
  extra = 0


class StrengthInline(admin.StackedInline):
  model = Strength
  extra = 0


class SocialLinkInline(admin.TabularInline):
  model = SocialLink
  extra = 0
  fields = ("position", "platform", "label", "url")


@admin.register(PortfolioPage)
class PortfolioPageAdmin(admin.ModelAdmin):
  list_display = ("name", "email", "phone", "updated_at")
  inlines = [FocusAreaInline, MetricInline, StrengthInline, SocialLinkInline]

  fieldsets = (
    ("Profile", {"fields": ("name", "headline", "hero_badge", "hero_description", "about_text")}),
    (
      "Section Headings",
      {
        "fields": (
          "about_eyebrow",
          "about_title",
          "skills_eyebrow",
          "skills_title",
          "projects_eyebrow",
          "projects_title",
          "experience_title",
          "education_title",
          "certifications_title",
          "contact_eyebrow",
        ),
      },
    ),
    ("Contact", {"fields": ("location", "email", "phone")}),
    ("Primary Social Links", {"fields": ("github_label", "github_url", "linkedin_label", "linkedin_url")}),
    ("Call To Action", {"fields": ("contact_title", "contact_description", "cv_filename")}),
  )

  def has_add_permission(self, request):
    if PortfolioPage.objects.exists():
      return False
    return super().has_add_permission(request)


class SkillEntryInline(admin.TabularInline):
  model = SkillEntry
  extra = 0


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
  list_display = ("title", "page", "position")
  list_editable = ("position",)
  list_filter = ("page",)
  inlines = [SkillEntryInline]


class ProjectStackItemInline(admin.TabularInline):
  model = ProjectStackItem
  extra = 0


class ProjectHighlightInline(admin.TabularInline):
  model = ProjectHighlight
  extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
  list_display = ("title", "page", "period", "has_url", "position")
  list_editable = ("position",)
  list_filter = ("page",)
  fields = ("page", "position", "title", "category", "period", "icon", "url", "description")
  inlines = [ProjectStackItemInline, ProjectHighlightInline]

  @admin.display(boolean=True, description="URL")
  def has_url(self, obj):
    return bool(obj.url)


@admin.register(ExperienceItem)
class ExperienceItemAdmin(admin.ModelAdmin):
  list_display = ("role", "organization", "period", "position")
  list_editable = ("position",)
  list_filter = ("page",)


@admin.register(EducationItem)
class EducationItemAdmin(admin.ModelAdmin):
  list_display = ("title", "organization", "period", "position")
  list_editable = ("position",)
  list_filter = ("page",)


@admin.register(CertificationItem)
class CertificationItemAdmin(admin.ModelAdmin):
  list_display = ("title", "page", "position")
  list_editable = ("position",)
  list_filter = ("page",)
