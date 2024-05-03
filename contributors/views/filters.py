import django_filters
from dateutil import relativedelta
from django import forms
from django.forms.widgets import TextInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from contributors.models import Contribution, ContributionLabel, Contributor
from contributors.utils import misc

STATE_CHOICES = (
    ('open', _('Open')),
    ('closed', _('Closed')),
)

PERIOD_CHOICES = (
    ('for_week', _('For week')),
    ('for_month', _('For month')),
    ('for_year', _('For year')),
)

CONTRIBUTORS_PERIOD_CHOICES = (
    ('all', _('Of all time')),
    ('for_month', _('For month')),
    ('for_week', _('For week')),
)


class ContributorsFilter(django_filters.FilterSet):
    """Contributors filter."""

    contributors_by_period = django_filters.ChoiceFilter(
        field_name='contribution__created_at',
        method='get_contributors_by_period',
        choices=CONTRIBUTORS_PERIOD_CHOICES,
        label='',
        widget=forms.Select,
        initial=CONTRIBUTORS_PERIOD_CHOICES[0],
        empty_label=None,
    )
    contributor_name = django_filters.CharFilter(
        field_name='contribution__contributor__login',
        lookup_expr='icontains',
        label='',
        widget=TextInput(attrs={'placeholder': _('Name')}),
    )
    organization = django_filters.CharFilter(
        field_name='contribution__repository__organization__name',
        lookup_expr='icontains',
        label='',
        widget=TextInput(attrs={'placeholder': _('Organization name')}),
    )

    class Meta:  # noqa: WPS306
        model = Contributor
        fields = [
            'contributors_by_period',
            'contributor_name',
            'organization',
        ]

    def get_contributors_by_period(self, queryset, name, value):  # noqa: WPS110, WPS615, E501
        """Contributions filter for a period."""
        if value == 'for_month':
            queryset = queryset.filter(
                contribution__created_at__gte=misc.datetime_month_ago(),
            ).distinct()
        elif value == 'for_week':
            queryset = queryset.filter(
                contribution__created_at__gte=misc.datetime_week_ago(),
            ).distinct()
        return queryset


class IssuesFilter(django_filters.FilterSet):
    """Issues filter."""

    info_title = django_filters.CharFilter(
        field_name='info__title',
        lookup_expr='icontains',
        label='',
        widget=TextInput(attrs={'placeholder': _('Title')}),
    )
    repository_full_name = django_filters.CharFilter(
        field_name='repository__full_name',
        lookup_expr='icontains',
        label='',
        widget=TextInput(attrs={'placeholder': _('Repository name')}),
    )
    repository_labels = django_filters.CharFilter(
        lookup_expr='icontains',
        field_name='repository__labels__name',
        label='',
        widget=TextInput(attrs={'placeholder': _('Language')}),
    )
    info_state = django_filters.ChoiceFilter(
        choices=STATE_CHOICES,
        lookup_expr='icontains',
        field_name='info__state',
        label='',
        empty_label=_('Status'),
    )

    good_first_issue_filter = django_filters.BooleanFilter(
        field_name='good_first_issue',
        method='get_good_first_issue',
        widget=forms.CheckboxInput,
        label='good first issue',
    )

    class Meta:  # noqa: WPS306
        model = Contribution
        fields = [
            'info_title',
            'repository_full_name',
            'repository_labels',
            'info_state',
        ]

    def get_good_first_issue(self, queryset, name, value):  # noqa: WPS110
        """Filter issues by label 'good_first_issue'."""
        good_first = ContributionLabel.objects.filter(
            name='good first issue',
        ).first()
        all_open_issues = Contribution.objects.filter(
            type='iss', info__state='open',
        )
        if good_first is None:
            queryset = all_open_issues.none()
        elif value:
            queryset = all_open_issues.filter(
                labels__in=[good_first.id],
            )
        return queryset


class DetailTablePeriodFilter(django_filters.FilterSet):
    """Period contributions filter."""

    period = django_filters.ChoiceFilter(
        choices=PERIOD_CHOICES,
        widget=forms.Select,
        method='get_contributions_by_period',
        initial=None,
        label=_('Period'),
        field_name='period_filter',
    )

    def get_contributions_by_period(self, queryset, name, value):  # noqa: WPS110, E501
        """Contributions filter for a period."""
        if value == 'for_year':
            datetime_now = timezone.now()
            date_eleven_months_ago = (
                datetime_now - relativedelta.relativedelta(
                    months=11, day=1,   # noqa: WPS432
                )
            ).date()
            queryset = queryset.filter(
                created_at__gte=date_eleven_months_ago,
            ).distinct()
        elif value == 'for_month':
            queryset = queryset.filter(
                created_at__gte=misc.datetime_month_ago(),
            ).distinct()
        elif value == 'for_week':
            queryset = queryset.filter(
                created_at__gte=misc.datetime_week_ago(),
            ).distinct()
        return queryset
