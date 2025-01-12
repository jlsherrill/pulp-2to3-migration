from django_filters.rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.decorators import action

from pulpcore.app.viewsets.base import DATETIME_FILTER_OPTIONS
from pulpcore.app.viewsets.custom_filters import (
    HyperlinkRelatedFilter,
    IsoDateTimeFilter
)

from pulpcore.plugin.serializers import AsyncOperationResponseSerializer
from pulpcore.plugin.tasking import enqueue_with_reservation
from pulpcore.plugin.viewsets import (
    BaseFilterSet,
    NamedModelViewSet,
    OperationPostponedResponse,
)

from .constants import PULP_2TO3_MIGRATION_RESOURCE
from .models import MigrationPlan, Pulp2Content
from .serializers import (
    MigrationPlanSerializer,
    MigrationPlanRunSerializer,
    Pulp2ContentSerializer
)
from .tasks.migrate import migrate_from_pulp2


class MigrationPlanViewSet(NamedModelViewSet,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin):
    """
    MigrationPlan ViewSet.
    """
    endpoint_name = 'migration-plans'
    queryset = MigrationPlan.objects.all()
    serializer_class = MigrationPlanSerializer

    @swagger_auto_schema(
        operation_summary="Run migration plan",
        operation_description="Trigger an asynchronous task to run a migration from Pulp 2.",
        responses={202: AsyncOperationResponseSerializer}
    )
    @action(detail=True, methods=('post',), serializer_class=MigrationPlanRunSerializer)
    def run(self, request, pk):
        """Run the migration plan."""
        migration_plan = self.get_object()
        serializer = MigrationPlanRunSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        validate = serializer.validated_data.get('validate', False)
        dry_run = serializer.validated_data.get('dry_run', False)
        result = enqueue_with_reservation(
            migrate_from_pulp2,
            [PULP_2TO3_MIGRATION_RESOURCE],
            kwargs={
                'migration_plan_pk': migration_plan.pk,
                'validate': validate,
                'dry_run': dry_run
            }
        )
        return OperationPostponedResponse(result, request)


class Pulp2ContentFilter(BaseFilterSet):
    """
    Filter for Pulp2Content ViewSet.
    """
    pulp2_id = filters.CharFilter()
    pulp2_content_type_id = filters.CharFilter()
    pulp2_last_updated = IsoDateTimeFilter(field_name='pulp2_last_updated')
    pulp3_content = HyperlinkRelatedFilter()

    class Meta:
        model = Pulp2Content
        fields = {
            'pulp2_id': ['exact', 'in'],
            'pulp2_content_type_id': ['exact', 'in'],
            'pulp2_last_updated': DATETIME_FILTER_OPTIONS,
            'pulp3_content': ['exact']
        }


class Pulp2ContentViewSet(NamedModelViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    ViewSet for Pulp2Content model.
    """
    endpoint_name = 'pulp2content'
    queryset = Pulp2Content.objects.all()
    serializer_class = Pulp2ContentSerializer
    filterset_class = Pulp2ContentFilter
