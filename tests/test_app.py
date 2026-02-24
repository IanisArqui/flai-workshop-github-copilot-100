"""
Tests for the Mergington High School API.

Every test follows the Arrange-Act-Assert (AAA) pattern:
  - Arrange: set up any preconditions or test data.
  - Act:     call the endpoint under test.
  - Assert:  verify the response and any resulting state changes.

The ``client`` fixture (defined in conftest.py) resets the in-memory
activities store before each test, so every test starts with a known,
clean state.
"""
import src.app as app_module


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

class TestRoot:
    def test_redirect_root(self, client):
        # Arrange - no specific setup required

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in (301, 302, 307, 308)
        assert response.headers["location"] == "/static/index.html"


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange - the fixture provides the full seeded dataset

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == len(app_module.activities)

    def test_activity_has_expected_fields(self, client):
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        for activity in response.json().values():
            assert expected_fields.issubset(activity.keys())


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in app_module.activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        # Arrange
        activity_name = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_signup_already_registered(self, client):
        # Arrange - pre-seed the participant so the duplicate case is triggered
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"
        app_module.activities[activity_name]["participants"].append(email)

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_unregister_success(self, client):
        # Arrange - pre-seed the participant so there is someone to remove
        activity_name = "Chess Club"
        email = "toleave@mergington.edu"
        app_module.activities[activity_name]["participants"].append(email)

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email not in app_module.activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        # Arrange
        activity_name = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_not_enrolled(self, client):
        # Arrange - use a valid activity but an email that is NOT enrolled
        activity_name = "Chess Club"
        email = "notenrolled@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
