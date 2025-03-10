from models import UserSession, PcObject
from tests.conftest import TestClient, clean_database
from tests.test_utils import create_user


class Get:
    class Returns200:
        @clean_database
        def expect_the_existing_user_session_to_be_deleted_deleted(self, app):
            # given
            user = create_user(email='test@mail.com')
            PcObject.save(user)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            assert auth_request.get('/bookings').status_code == 200

            # when
            response = auth_request.get('/users/signout')

            # then
            assert response.status_code == 200
            session = UserSession.query.filter_by(userId=user.id).first()
            assert session is None
