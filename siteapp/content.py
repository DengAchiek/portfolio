from django.db import transaction
from django.db.models import Prefetch

from . import defaults
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
  SkillCategory,
  SkillEntry,
  Strength,
)


def seed_portfolio_content():
  if PortfolioPage.objects.exists():
    return PortfolioPage.objects.first()

  with transaction.atomic():
    page = PortfolioPage.objects.create(**defaults.PAGE_DEFAULTS)

    FocusArea.objects.bulk_create(
      [FocusArea(page=page, position=index, label=item) for index, item in enumerate(defaults.FOCUS_AREAS, start=1)],
    )
    Metric.objects.bulk_create(
      [Metric(page=page, position=index, value=item["value"], label=item["label"]) for index, item in enumerate(defaults.METRICS, start=1)],
    )
    Strength.objects.bulk_create(
      [
        Strength(page=page, position=index, title=item["title"], description=item["description"])
        for index, item in enumerate(defaults.STRENGTHS, start=1)
      ],
    )

    for skill_index, skill in enumerate(defaults.SKILLS, start=1):
      skill_obj = SkillCategory.objects.create(
        page=page,
        position=skill_index,
        title=skill["title"],
        icon=skill["icon"],
        summary=skill["summary"],
      )
      SkillEntry.objects.bulk_create(
        [
          SkillEntry(skill=skill_obj, position=entry_index, label=entry)
          for entry_index, entry in enumerate(skill["entries"], start=1)
        ],
      )

    for project_index, project in enumerate(defaults.PROJECTS, start=1):
      project_obj = Project.objects.create(
        page=page,
        position=project_index,
        title=project["title"],
        category=project["category"],
        period=project["period"],
        icon=project["icon"],
        url=project.get("url", ""),
        description=project["description"],
      )
      ProjectStackItem.objects.bulk_create(
        [
          ProjectStackItem(project=project_obj, position=stack_index, label=entry)
          for stack_index, entry in enumerate(project["stack"], start=1)
        ],
      )
      ProjectHighlight.objects.bulk_create(
        [
          ProjectHighlight(project=project_obj, position=highlight_index, text=entry)
          for highlight_index, entry in enumerate(project["highlights"], start=1)
        ],
      )

    ExperienceItem.objects.bulk_create(
      [
        ExperienceItem(
          page=page,
          position=index,
          role=item["role"],
          organization=item["organization"],
          period=item["period"],
          description=item["description"],
        )
        for index, item in enumerate(defaults.EXPERIENCE, start=1)
      ],
    )
    EducationItem.objects.bulk_create(
      [
        EducationItem(
          page=page,
          position=index,
          title=item["title"],
          organization=item["organization"],
          period=item["period"],
        )
        for index, item in enumerate(defaults.EDUCATION, start=1)
      ],
    )
    CertificationItem.objects.bulk_create(
      [
        CertificationItem(page=page, position=index, title=item)
        for index, item in enumerate(defaults.CERTIFICATIONS, start=1)
      ],
    )

  return page


def get_portfolio_page():
  queryset = PortfolioPage.objects.prefetch_related(
    "focus_areas",
    "metrics",
    "strengths",
    "experience_items",
    "education_items",
    "certification_items",
    "social_links",
    Prefetch("skills", queryset=SkillCategory.objects.prefetch_related("entries")),
    Prefetch("projects", queryset=Project.objects.prefetch_related("stack_items", "highlights")),
  )
  page = queryset.first()
  if page is None:
    seed_portfolio_content()
    page = queryset.first()
  return page


def resolve_social_label(label, fallback):
  cleaned = (label or "").strip()
  if not cleaned or cleaned.lower() == f"add {fallback.lower()} link":
    return fallback
  return cleaned


def append_social_link(links, seen, *, label, url, icon):
  if not url:
    return
  key = (icon, url)
  if key in seen:
    return
  seen.add(key)
  links.append({"label": label, "url": url, "icon": icon})


def build_portfolio_context(page):
  social_links = []
  seen_social_links = set()
  append_social_link(
    social_links,
    seen_social_links,
    label=resolve_social_label(page.github_label, "GitHub"),
    url=page.github_url,
    icon="github",
  )
  append_social_link(
    social_links,
    seen_social_links,
    label=resolve_social_label(page.linkedin_label, "LinkedIn"),
    url=page.linkedin_url,
    icon="linkedin",
  )
  for link in page.social_links.all():
    append_social_link(
      social_links,
      seen_social_links,
      label=resolve_social_label(link.label, link.get_platform_display()),
      url=link.url,
      icon=link.platform,
    )

  profile = {
    "name": page.name,
    "headline": page.headline,
    "badge_text": page.hero_badge,
    "hero_description": page.hero_description,
    "summary": page.about_text,
    "contact_title": page.contact_title,
    "contact_description": page.contact_description,
    "location": page.location,
    "email": page.email,
    "email_href": page.email_href,
    "phone": page.phone,
    "phone_href": page.phone_href,
    "github_label": resolve_social_label(page.github_label, "GitHub"),
    "github_url": page.github_url,
    "linkedin_label": resolve_social_label(page.linkedin_label, "LinkedIn"),
    "linkedin_url": page.linkedin_url,
    "social_links": social_links,
    "cv_filename": page.cv_filename,
  }

  sections = {
    "about_eyebrow": page.about_eyebrow,
    "about_title": page.about_title,
    "skills_eyebrow": page.skills_eyebrow,
    "skills_title": page.skills_title,
    "projects_eyebrow": page.projects_eyebrow,
    "projects_title": page.projects_title,
    "experience_title": page.experience_title,
    "education_title": page.education_title,
    "certifications_title": page.certifications_title,
    "contact_eyebrow": page.contact_eyebrow,
  }

  skills = [
    {
      "title": skill.title,
      "icon": skill.icon,
      "summary": skill.summary,
      "entries": [entry.label for entry in skill.entries.all()],
    }
    for skill in page.skills.all()
  ]

  projects = [
    {
      "title": project.title,
      "category": project.category,
      "period": project.period,
      "icon": project.icon,
      "url": project.url,
      "description": project.description,
      "stack": [entry.label for entry in project.stack_items.all()],
      "highlights": [entry.text for entry in project.highlights.all()],
    }
    for project in page.projects.all()
  ]

  experience = [
    {
      "role": item.role,
      "organization": item.organization,
      "period": item.period,
      "description": item.description,
    }
    for item in page.experience_items.all()
  ]

  education = [
    {
      "title": item.title,
      "org": item.organization,
      "period": item.period,
    }
    for item in page.education_items.all()
  ]

  return {
    "page": page,
    "profile": profile,
    "sections": sections,
    "focus_areas": [item.label for item in page.focus_areas.all()],
    "metrics": [{"value": item.value, "label": item.label} for item in page.metrics.all()],
    "strengths": [{"title": item.title, "description": item.description} for item in page.strengths.all()],
    "skills": skills,
    "projects": projects,
    "experience": experience,
    "education": education,
    "certifications": [item.title for item in page.certification_items.all()],
  }
