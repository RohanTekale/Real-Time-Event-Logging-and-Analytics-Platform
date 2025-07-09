from django.db import models
from django.contrib.auth.models import User

# creating an model named Event
class Event(models.Model):
    # deciding event types
    EVENT_TYPE = (
        ('user_action', 'User Action'),
        ('system_event', 'System Event'),
        ('error', 'Error'),
        ('purchase', 'Purchase'),
    )  #four types of events user_action, system_events, error, purchase

    # Status of events
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ) # three status pending, success, failed
    

    # deciding data type of each field
    type = models.CharField(max_length=20, choices=EVENT_TYPE)
    source = models.CharField(max_length=50)
    data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type}- {self.status}"

# creating amodel UserProfile
class UserProfile(models.Model):
    ROLES = (
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
    )
    #user field should be one to one 
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    #default user role  set to analyst
    role = models.CharField(max_length=20, choices=ROLES, default='analyst') 

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# creating a model for SystemMetrics
class SystemMetrics(models.Model):
    # deciding data type of each field
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    network_in = models.FloatField()
    network_out = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"System Metrics - {self.timestamp}"

class MLInsight(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ml_insights')
    sentiment = models.CharField(max_length=50)
    confidence = models.FloatField()
    anomaly_score = models.FloatField()
    prediction = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight for Event {self.event.id} - {self.sentiment}"