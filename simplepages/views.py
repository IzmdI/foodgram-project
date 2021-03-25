from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = "simplepages/author.html"


class AboutTechView(TemplateView):
    template_name = "simplepages/tech.html"
