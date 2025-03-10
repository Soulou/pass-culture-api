from decimal import Decimal
from typing import List, Union

from models.booking import Booking
from models.product import Product
from models.offer_type import ThingType

PHYSICAL_EXPENSES_CAPPED_TYPES = [
    ThingType.AUDIOVISUEL,
    ThingType.INSTRUMENT,
    ThingType.JEUX,
    ThingType.LIVRE_EDITION,
    ThingType.MUSIQUE
]
DIGITAL_EXPENSES_CAPPED_TYPES = [
    ThingType.AUDIOVISUEL,
    ThingType.JEUX_VIDEO,
    ThingType.MUSIQUE,
    ThingType.PRESSE_ABO
]

SUBVENTION_TOTAL = Decimal(500)
SUBVENTION_PHYSICAL_THINGS = Decimal(200)
SUBVENTION_DIGITAL_THINGS = Decimal(200)


def get_expenses(bookings: List[Booking]) -> dict:
    total_expenses = _compute_booking_expenses(bookings)
    physical_expenses = _compute_booking_expenses(bookings, _get_bookings_of_physical_things)
    digital_expenses = _compute_booking_expenses(bookings, _get_bookings_of_digital_things)

    return {
        'all': {'max': SUBVENTION_TOTAL, 'actual': total_expenses},
        'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': physical_expenses},
        'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': digital_expenses}
    }


def _compute_booking_expenses(bookings: List[Booking], get_bookings=lambda b: b) -> Decimal:
    bookings_to_sum = filter(lambda b: not b.isCancelled, get_bookings(bookings))
    expenses = map(lambda b: b.value, bookings_to_sum)
    return Decimal(sum(expenses))


def _get_bookings_of_digital_things(bookings: List[Booking]) -> List[Booking]:
    match = []
    for booking in bookings:
        product = booking.stock.resolvedOffer.product
        if is_eligible_to_digital_products_capping(product):
            match.append(booking)

    return match


def _get_bookings_of_physical_things(bookings: List[Booking]) -> List[Booking]:
    match = []
    for booking in bookings:
        product = booking.stock.resolvedOffer.product
        if is_eligible_to_physical_products_capping(product):
            match.append(booking)

    return match


def is_eligible_to_digital_products_capping(product: Product) -> bool:
    if product.isDigital and product.type in map(str, DIGITAL_EXPENSES_CAPPED_TYPES):
        return True

    return False


def is_eligible_to_physical_products_capping(product: Product) -> bool:
    if product.isDigital and product.type == str(ThingType.LIVRE_EDITION):
        return True

    if not product.isDigital and product.type in map(str, PHYSICAL_EXPENSES_CAPPED_TYPES):
        return True

    return False
