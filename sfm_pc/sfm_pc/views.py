from django.views.generic.base import TemplateView


class Dashboard(TemplateView):
    template_name = 'sfm_pc/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)

        return context
