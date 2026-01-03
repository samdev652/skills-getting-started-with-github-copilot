"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball": {
            "description": "Team sport focusing on skills, strategy, and athletic development",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Individual and doubles tennis coaching and match play",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["jessica@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art techniques",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["rachel@mergington.edu", "noah@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Orchestra and band performance opportunities",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced mathematics problem-solving and competition preparation",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["ryan@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball" in data
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup for a new student"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student_fails(self, client):
        """Test that signing up a duplicate student fails"""
        # First signup
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Second signup should fail
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up"
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_success(self, client):
        """Test successful unregistration of an existing student"""
        # First, add a student
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Chess Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered test@mergington.edu from Chess Club"
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_student_fails(self, client):
        """Test that unregistering a student who isn't registered fails"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from a nonexistent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_preset_participant(self, client):
        """Test unregistering a participant who was already in the activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test a complete signup and unregister workflow"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify count increased
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify count returned to original
        after_unregister = client.get("/activities")
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
    
    def test_multiple_students_signup_same_activity(self, client):
        """Test multiple students can sign up for the same activity"""
        activity = "Basketball"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all students are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
