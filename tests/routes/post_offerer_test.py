from unittest.mock import patch

from models import PcObject, Offerer, RightsType, UserOfferer
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, create_user_offerer, create_offerer


class Post:
    class Returns201:
        @clean_database
        def when_creating_a_virtual_venue(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json['siren'] == '418166096'
            assert response.json['name'] == 'Test Offerer'
            virtual_venues = list(filter(lambda v: v['isVirtual'],
                                         response.json['managedVenues']))
            assert len(virtual_venues) == 1

        @clean_database
        def when_no_address_is_provided(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json['siren'] == '418166096'
            assert response.json['name'] == 'Test Offerer'

        @clean_database
        def when_current_user_is_admin(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=True)
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201

        @clean_database
        def expect_the_current_user_to_be_editor_of_the_new_offerer(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.UserOfferers[0].rights == RightsType.editor

        @patch('domain.admin_emails.write_object_validation_email', return_value={
                    'Html-part': None,
                    })
        @clean_database
        def when_offerer_already_have_user_offerer_new_user_offerer_has_validation_token(self,
                                                                                         write_object_validation_email,
                                                                                         app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            user_2 = create_user(email="other_offerer@mail.com", is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_2, offerer, validation_token=None)
            PcObject.save(user, user_2, offerer, user_offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            created_user_offerer = UserOfferer.query\
                .filter(UserOfferer.offerer == offerer)\
                .filter(UserOfferer.user == user)\
                .one()
            assert created_user_offerer.validationToken is not None


        @clean_database
        @patch('domain.admin_emails.write_object_validation_email',
               return_value={'Html-part': None})
        def expect_new_offerer_to_have_validation_token_but_user_offerer_dont(self,
                                                                              write_object_validation_email,
                                                                              app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.validationToken is not None
            assert offerer.UserOfferers[0].validationToken is None

        @clean_database
        @patch('domain.admin_emails.write_object_validation_email',
               return_value={'Html-part': None})
        def when_offerer_already_in_base_just_create_user_offerer_with_validation_token(self,
                                                                                        write_object_validation_email,
                                                                                        app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789')
            PcObject.save(user, offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # Then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.UserOfferers[0].rights == RightsType.editor
            assert offerer.UserOfferers[0].validationToken is not None

        @clean_database
        @patch('domain.admin_emails.write_object_validation_email',
               return_value={'Html-part': None})
        def expect_not_validated_offerer_to_keeps_validation_token_and_user_offerer_get_one(self,
                                                                                              write_object_validation_email,
                                                                                              app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789', validation_token='not_validated')
            PcObject.save(user, offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.validationToken == 'not_validated'
            assert offerer.UserOfferers[0].validationToken is not None
