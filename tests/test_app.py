import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test the activities endpoints"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activity_structure(self):
        """Test that activity has expected structure"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@example.com" in result["message"]

    def test_signup_duplicate_participant(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@example.com"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_from_activity(self):
        """Test unregistering from an activity"""
        email = "unregister@example.com"
        
        # Sign up first
        client.post(f"/activities/Tennis Club/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/Tennis Club/unregister?email={email}"
        )
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant who isn't registered"""
        response = client.post(
            "/activities/Art Studio/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_participant_count_after_signup(self):
        """Test that participant count increases after signup"""
        activity_name = "Debate Team"
        email = "count@example.com"
        
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get updated count
        response2 = client.get("/activities")
        new_count = len(response2.json()[activity_name]["participants"])
        
        assert new_count == initial_count + 1

    def test_participant_count_after_unregister(self):
        """Test that participant count decreases after unregister"""
        activity_name = "Robotics Club"
        email = "uncount@example.com"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get count after signup
        response1 = client.get("/activities")
        signup_count = len(response1.json()[activity_name]["participants"])
        
        # Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        
        # Get count after unregister
        response2 = client.get("/activities")
        unregister_count = len(response2.json()[activity_name]["participants"])
        
        assert unregister_count == signup_count - 1
