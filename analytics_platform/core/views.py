from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import Event, UserProfile, SystemMetrics, MLInsight
from .serializers import EventSerializer, Userserializer, SystemMetricsSerializer, AnalyticsSerializer, MLInsightSerializer
from .tasks import process_event, collect_system_metrics, generate_ml_insights, detect_anaomalies, predict_traffic
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count
import docker
from .permissions import IsAdmin, IsAnalyst  

class UserCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = Userserializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password'],
            )
            UserProfile.objects.create(user=user, role=request.data['role'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'role': request.user.userprofile.role})


class EventSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            process_event.delay(event.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalyticsMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        end_time = timezone.now()
        start_time = end_time - timedelta(seconds=60)
        events = Event.objects.filter(created_at__range=[start_time, end_time])
        event_count = events.count()
        active_users = events.values('data__user_id').distinct().count()
        failed_count = events.filter(status='failed').count()
        error_rate = failed_count / event_count if event_count else 0
        data = {
            'events_per_second': event_count / 3600.0,  # Over last hour
            'active_users': active_users,
            'error_rate': error_rate,
            'timestamp': end_time
        }
        serializer = AnalyticsSerializer(data)
        return Response(serializer.data)


class EventAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        events = Event.objects.all()
        if start_date and end_date:
            events = events.filter(created_at__range=[start_date, end_date])
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)


class MLinsigthsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fire off task
        generate_ml_insights.delay()

        # Return recent stored insights if available
        insights = MLInsight.objects.all().order_by('-created_at')[:10]
        serializer = MLInsightSerializer(insights, many=True)

        return Response({
            "message": "ML insights generation task has been triggered successfully.",
            "recent_insights": serializer.data
        })


class AnomalyDetectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        time_range = request.data.get('time_range', '1h')
        threshold = float(request.data.get('threshold', 2.5))

        detect_anaomalies.delay(time_range, threshold)

        return Response({
            "message": "Anomaly detection task has been triggered successfully.",
            "note": "Check DB or logs for results."
        })


class TrafficPredictionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hours = int(request.query_params.get('hours', 24))

        predict_traffic.delay(hours)

        return Response({
            "message": "Traffic prediction task triggered successfully.",
            "note": "Check DB or logs for output."
        })


class SystemHealthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        collect_system_metrics.delay()

        metrics = SystemMetrics.objects.last()
        serializer = SystemMetricsSerializer(metrics)

        return Response({
            "message": "System health metrics collection triggered.",
            "latest_metrics": serializer.data
        })


class ContainerStatusView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)
            status = [{'name': c.name, 'status': c.status} for c in containers]
            return Response(status)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)