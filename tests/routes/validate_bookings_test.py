from datetime import datetime, timedelta
from urllib.parse import urlencode

from models import PcObject, EventType, ThingType, Deposit, Booking, User
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_offer_with_thing_product, create_deposit, create_stock_with_event_offer, \
    create_venue, \
    create_offerer, \
    create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer, create_stock_from_offer
from utils.human_ids import humanize


class Patch:
    def setup_class(cls):
        cls.tomorrow = datetime.utcnow() + timedelta(days=1)
        cls.tomorrow_plus_one_hour = cls.tomorrow + timedelta(hours=1)
        cls.tomorrow_minus_one_hour = cls.tomorrow - timedelta(hours=1)

    class Returns204:
        @clean_database
        def when_user_has_rights(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=Patch.tomorrow,
                                                  end_datetime=Patch.tomorrow_plus_one_hour,
                                                  booking_limit_datetime=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            booking_id = booking.id
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 204
            assert Booking.query.get(booking_id).isUsed
            assert Booking.query.get(booking_id).dateUsed is not None

        @clean_database
        def when_header_is_not_standard_but_request_is_valid(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=Patch.tomorrow,
                                                  end_datetime=Patch.tomorrow_plus_one_hour,
                                                  booking_limit_datetime=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            booking_id = booking.id
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@email.fr') \
                .patch(url, headers={'origin': 'http://random_header.fr'})

            # Then
            assert response.status_code == 204
            assert Booking.query.get(booking_id).isUsed

        @clean_database
        def when_booking_user_email_has_special_character_url_encoded(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            user_admin = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer, beginning_datetime=Patch.tomorrow,
                                                       end_datetime=Patch.tomorrow_plus_one_hour)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0,
                                                       booking_limit_date=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(user_offerer, booking)
            url_email = urlencode({'email': 'user+plus@email.fr'})
            url = '/bookings/token/{}?{}'.format(booking.token, url_email)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)
            # Then
            assert response.status_code == 204

        @clean_database
        def when_user_patching_is_global_admin_is_activation_event_and_no_deposit_for_booking_user(self, app):
            # Given
            user = create_user(is_admin=False, can_book_free_offers=False)
            pro_user = create_user(email='pro@email.fr', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer, beginning_datetime=Patch.tomorrow,
                                                                  end_datetime=Patch.tomorrow_plus_one_hour)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0,
                                                       booking_limit_date=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            user_id = user.id
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            user = User.query.get(user_id)
            assert response.status_code == 204
            assert user.canBookFreeOffers
            deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
            assert len(deposits_for_user) == 1
            assert deposits_for_user[0].amount == 500
            assert user.canBookFreeOffers

        @clean_database
        def when_user_patching_is_global_admin_is_activation_thing_and_no_deposit_for_booking_user(self, app):
            # Given
            user = create_user(is_admin=False, can_book_free_offers=False)
            pro_user = create_user(email='pro@email.fr', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer, beginning_datetime=Patch.tomorrow,
                                                                  end_datetime=Patch.tomorrow_plus_one_hour)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0,
                                                       booking_limit_date=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            user_id = user.id
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            user = User.query.get(user_id)
            assert response.status_code == 204
            assert user.canBookFreeOffers
            deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
            assert len(deposits_for_user) == 1
            assert deposits_for_user[0].amount == 500
            assert user.canBookFreeOffers

    class Returns403:
        @clean_database
        def when_user_not_editor_and_valid_email(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=Patch.tomorrow,
                                                  end_datetime=Patch.tomorrow_plus_one_hour,
                                                  booking_limit_datetime=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, admin_user)
            booking_id = booking.id
            url = '/bookings/token/{}?email={}'.format(booking.token, user.email)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 403
            assert response.json['global'] == [
                "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
            assert not Booking.query.get(booking_id).isUsed

        @clean_database
        def when_booking_beginning_datetime_in_more_than_72_hours(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            four_days_from_now = datetime.utcnow() + timedelta(days=4)
            stock = create_stock_from_offer(offer, price=0, beginning_datetime=four_days_from_now)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 403
            assert response.json['beginningDatetime'] == [
                'Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l\'évènement']

        @clean_database
        def when_it_is_an_offer_on_an_activation_event_and_user_patching_is_not_global_admin(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr', is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
            activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer, beginning_datetime=Patch.tomorrow,
                                                                  end_datetime=Patch.tomorrow_plus_one_hour)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0,
                                                       booking_limit_date=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 403

    class Returns404:
        @clean_database
        def when_user_not_editor_and_invalid_email(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=Patch.tomorrow,
                                                  end_datetime=Patch.tomorrow_plus_one_hour,
                                                  booking_limit_datetime=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, admin_user)
            booking_id = booking.id
            url = '/bookings/token/{}?email={}'.format(booking.token, 'wrong@email.fr')

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 404
            assert Booking.query.get(booking_id).isUsed == False

        @clean_database
        def when_booking_user_email_with_special_character_not_url_encoded(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            user_admin = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer, beginning_datetime=Patch.tomorrow,
                                                       end_datetime=Patch.tomorrow_plus_one_hour)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0,
                                                       booking_limit_date=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(user_offerer, booking)
            url = '/bookings/token/{}?email={}'.format(booking.token, user.email)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 404

        @clean_database
        def when_user_not_editor_and_valid_email_but_invalid_offer_id(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=Patch.tomorrow,
                                                  end_datetime=Patch.tomorrow_plus_one_hour,
                                                  booking_limit_datetime=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, admin_user)
            booking_id = booking.id
            url = '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, user.email, humanize(123))

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 404
            assert not Booking.query.get(booking_id).isUsed

    class Returns405:
        @clean_database
        def when_user_patching_is_global_admin_is_activation_offer_and_existing_deposit_for_booking_user(
                self,
                app):
            # Given
            user = create_user(is_admin=False, can_book_free_offers=False)
            pro_user = create_user(email='pro@email.fr', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer, beginning_datetime=Patch.tomorrow,
                                                                  end_datetime=Patch.tomorrow_plus_one_hour)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0,
                                                       booking_limit_date=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            deposit = create_deposit(user, amount=500)
            PcObject.save(booking, user_offerer, deposit)
            user_id = user.id
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            deposits_for_user = Deposit.query.filter_by(userId=user_id).all()
            assert response.status_code == 405
            assert len(deposits_for_user) == 1
            assert deposits_for_user[0].amount == 500

    class Returns410:
        @clean_database
        def when_booking_is_cancelled(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=Patch.tomorrow,
                                                  end_datetime=Patch.tomorrow_plus_one_hour,
                                                  booking_limit_datetime=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            booking.isCancelled = True
            PcObject.save(booking, user_offerer)
            booking_id = booking.id
            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a été annulée']
            assert not Booking.query.get(booking_id).isUsed

        @clean_database
        def when_booking_already_validated(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=Patch.tomorrow,
                                                  end_datetime=Patch.tomorrow_plus_one_hour,
                                                  booking_limit_datetime=Patch.tomorrow_minus_one_hour)
            booking = create_booking(user, stock, venue=venue)
            booking.isUsed = True
            PcObject.save(booking, user_offerer)
            booking_id = booking.id

            url = '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a déjà été validée']
            assert Booking.query.get(booking_id).isUsed
