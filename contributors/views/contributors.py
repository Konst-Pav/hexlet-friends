from django_filters.views import FilterView

from contributors.models import Contributor
from contributors.views.filters import ContributorsFilter
from contributors.views.mixins import TableSortSearchAndPaginationMixin


class ListView(
    TableSortSearchAndPaginationMixin,
    FilterView,
):
    """A list of contributors with contributions."""

    template_name = 'contributors_list.html'
    filterset_class = ContributorsFilter
    sortable_fields = (
        'login',
        'name',
        'commits',
        'additions',
        'deletions',
        'pull_requests',
        'issues',
        'comments',
    )
    searchable_fields = ('login', 'name')
    ordering = sortable_fields[0]

    def get_queryset(self):  # noqa: WPS615
        """Add queryset."""
        queryset = Contributor.objects.visible().with_contributions()
        self.filterset = self.filterset_class(
            self.request.GET,
            queryset=queryset,
        )
        return self.filterset.qs.distinct()
