from datetime import datetime, timedelta

import pytest

from models import Booking, Offer, Stock, User, Product, PcObject, ApiErrors
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type, create_offerer, create_venue, \
    create_offer_with_thing_product, create_stock_from_offer, create_user, create_booking


def test_booking_completed_url_gets_normalized():
    # Given

    product = Product()
    product.url = 'javascript:alert("plop")'

    offer = Offer()
    offer.id = 1
    offer.product = product

    stock = Stock()

    user = User()
    user.email = 'bob@bob.com'

    booking = Booking()
    booking.token = 'ABCDEF'
    booking.stock = stock
    booking.stock.offer = offer
    booking.user = user

    # When
    completedUrl = booking.completedUrl

    # Then
    assert completedUrl == 'http://javascript:alert("plop")'

@clean_database
def test_raises_error_on_booking_when_existing_booking_is_used_and_booking_date_is_after_last_update_on_stock(app):
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, price=0, available=1)
    user1 = create_user(email='used_booking@booking.com')
    user2 = create_user(email='booked@email.com')
    PcObject.save(stock)
    date_after_stock_last_update = datetime.utcnow()
    booking1 = create_booking(user1,
                              stock,
                              date_used=date_after_stock_last_update,
                              is_cancelled=False,
                              is_used=True)
    PcObject.save(booking1)
    date_after_last_booking = datetime.utcnow()
    booking2 = create_booking(user2,
                              stock,
                              date_used=date_after_last_booking,
                              is_cancelled=False,
                              is_used=False)

    # When
    with pytest.raises(ApiErrors) as e:
        PcObject.save(booking2)

    # Then
    assert e.value.errors['global'] == ['la quantité disponible pour cette offre est atteinte']


class BookingIsCancellableTest:
    def test_booking_on_event_with_begining_date_in_more_than_72_hours_is_cancellable(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=73)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable

    def test_booking_on_thing_is_cancellable(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.offer = Offer()
        booking.stock.offer.product = create_product_with_thing_type()

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == True

    def test_booking_on_event_is_not_cancellable_if_begining_date_time_before_72_hours(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=71)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == False


class StatusLabelTest:
    def test_is_cancelled_label_when_booking_is_cancelled(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.isCancelled = True

        # When
        statusLabel = booking.statusLabel

        # Then
        assert statusLabel == "Réservation annulée"

    def test_is_countermak_validated_label_when_booking_is_used(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.isUsed = True

        # When
        statusLabel = booking.statusLabel

        # Then
        assert statusLabel == 'Contremarque validée'

    def test_validated_label_when_event_is_expired(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(-1)

        # When
        statusLabel = booking.statusLabel

        # Then
        assert statusLabel == 'Validé'
