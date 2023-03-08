from django_filters import CharFilter, FilterSet
from .models import Article


class OrderFilter(FilterSet):

	review = CharFilter(field_name='average_review', lookup_expr='gte 1')

	class Meta:
		model = Article
		fields = '__all__'
