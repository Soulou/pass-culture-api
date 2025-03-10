from models.booking import Booking
from models.payment import Payment
from models.offer import Offer
from models.offerer import Offerer
from models.stock import Stock
from models.user import User
from models.user_offerer import UserOfferer
from models.venue import Venue
from sandboxes.scripts.utils.helpers import get_booking_helper, \
    get_offer_helper, \
    get_offerer_helper, \
    get_payment_helper, \
    get_stock_helper, \
    get_user_helper, \
    get_venue_helper

def get_existing_pro_validated_user_with_validated_offerer_with_reimbursement():
    query = Payment.query.join(Booking) \
                         .join(Stock) \
                         .join(Offer) \
                         .join(Venue) \
                         .join(Offerer) \
                         .join(UserOfferer) \
                         .filter(
                            (Offerer.validationToken == None) & \
                            (UserOfferer.validationToken == None)
                         ) \
                         .join(User) \
                         .filter(User.validationToken == None)

    payment =  query.first()
    booking = payment.booking
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    offerer = venue.managingOfferer
    user = [
        uo.user
        for uo in offerer.UserOfferers
        if uo.user.validationToken == None
    ][0]
    return {
        "booking": get_booking_helper(booking),
        "offer": get_offer_helper(offer),
        "offerer": get_offerer_helper(offerer),
        "payment": get_payment_helper(payment),
        "stock": get_stock_helper(stock),
        "user": get_user_helper(user),
        "venue": get_venue_helper(venue)
    }
