from celery import shared_task
from sklearn.ensemble import IsolationForest
from transformers import pipeline
import numpy as np
from .models import Event,SystemMetrics
import psutil
from datetime import datetime, timedelta
from django.db.models import Count
from langchain.prompts import PromptTemplate
from langchain.llms import huggingface_hub
import os


@shared_task
def process_event(event_id):
    event = Event.objects.get(id=event_id)
    try:
        # Process the event
        event.status = 'success'
        event.save()
    except Exception as e:
        event.status = 'failedx'
        event.save()
@shared_task
def collect_system_metrics():
    # Collect system metrics
    SystemMetrics.objects.create(
        cpu_usage=psutil.cpu_percent(),
        memory_usage=psutil.virtual_memory().percent,
        disk_usage=psutil.disk_usage('/').percent,
        network_in = psutil.net_io_counters().bytes_recv,
        network_out = psutil.net_io_counters().bytes_sent,
    )
@shared_task
def generate_ml_insights():
    classifier = pipeline('sentiment-analysis')  
    events = Event.objects.filter(type='user_action')[:10]
    insights = []
    for event in events:
        text = str(event.data)
        result = classifier(text)[0]
        insights.append({
            'event_id': event.id,
            'sentiment': result['label'],
            'confidence': result['score'],
            'anomaly_score': 0.0,
            'prediction':0.0,
        })
    return insights

@shared_task
def detect_anaomalies(time_range='1h'):
    # Get the system metrics for the given time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=int(time_range[:-1]))
    events = Event.objects.filter(created_at__range=(start_time,end_time))
    # Detect anomalies
    if not events.exists():
        return {'anamolies':[]}
    data = np.array([e.id] for e in events)
    model = IsolationForest(contamination=0.1)
    model.fit(data)
    anamolies = model.predict(data)
    return {'anamolies':anamolies.tolist()}

@shared_task
def predict_traffic(hours=24):
    # Get the system metrics for the given time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    events = Event.objects.filter(created_at__range=(start_time,end_time))
    # Predict traffic
    event_counts = events.values('type').annotate(count=Count('id'))
    prediction = sum(c['count'] for c in event_counts)* hours/24
    return {'prediction_events':prediction}
