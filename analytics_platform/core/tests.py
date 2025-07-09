import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import UserProfile, Event
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

@pytest.mark.django_db
def test_login_view():
    client = APIClient()
    user = User.objects.create_user(username='testuser', password='testpass')
    UserProfile.objects.create(user=user, role='analyst')
    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert response.data['role'] == 'analyst'

@pytest.mark.django_db
def test_user_create_view():
    client = APIClient()
    admin = User.objects.create_user(username='admin', password='adminpass')
    UserProfile.objects.create(user=admin, role='admin')
    token = RefreshToken.for_user(admin).access_token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.post(reverse('user_create'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass',
        'role': 'analyst'
    })
    assert response.status_code == 201
    assert User.objects.filter(username='newuser').exists()

@pytest.mark.django_db
def test_event_submit_view():
    client = APIClient()
    user = User.objects.create_user(username='testuser', password='testpass')
    UserProfile.objects.create(user=user, role='analyst')
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.post(reverse('event_submit'), {
        'type': 'user_action',
        'source': 'web_app',
        'data': {'user_id': '12345'},
        'status': 'pending'
    })
    assert response.status_code == 201
    assert Event.objects.filter(type='user_action').exists()

@pytest.mark.django_db
def test_analytics_metrics_view():
    client = APIClient()
    user = User.objects.create_user(username='testuser', password='testpass')
    UserProfile.objects.create(user=user, role='analyst')
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    Event.objects.create(type='user_action', source='web_app', data={'user_id': '12345'}, status='success')
    response = client.get(reverse('analytics_metrics'))
    assert response.status_code == 200
    assert 'events_per_second' in response.data