from typing import List, Tuple

import pandas
from sqlalchemy import text, func

from models import Offerer, UserOfferer, Venue, Offer, Stock, Booking, EventType, ThingType, User
from models.db import db
from repository.booking_queries import count_all_bookings, \
    count_all_cancelled_bookings as query_count_all_cancelled_bookings, count_bookings_by_departement, \
    count_all_cancelled_bookings_by_departement, _query_get_used_or_finished_bookings_on_non_activation_offers
from repository.offer_queries import get_active_offers_ids_query
from repository.offerer_queries import count_offerer, count_offerer_with_stock, count_offerer_by_departement, \
    count_offerer_with_stock_by_departement


def get_offerer_count(departement_code: str = None) -> int:
    return count_offerer_by_departement(departement_code) if departement_code else count_offerer()


def get_offerer_with_stock_count(departement_code: str = None) -> int:
    return count_offerer_with_stock_by_departement(departement_code) if departement_code else count_offerer_with_stock()


def get_offerers_with_offer_available_on_discovery_count(departement_code: str = None) -> int:
    active_offers_ids = get_active_offers_ids_query()
    query = Offerer.query.join(Venue).join(Offer).filter(Offer.id.in_(active_offers_ids))

    if departement_code:
        query = query \
            .filter(Venue.departementCode == departement_code)

    return query \
        .distinct(Offerer.id) \
        .count()


def get_offerers_with_non_cancelled_bookings_count(departement_code: str = None) -> int:
    query = Offerer.query.join(Venue)

    if departement_code:
        query = query.filter(Venue.departementCode == departement_code)

    return query \
        .join(Offer) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .filter(Offer.type != str(EventType.ACTIVATION)) \
        .join(Stock) \
        .join(Booking) \
        .filter_by(isCancelled=False) \
        .distinct(Offerer.id) \
        .count()


def get_offers_with_user_offerer_and_stock_count(departement_code: str = None) -> int:
    query = Offer.query.join(Venue)

    if departement_code:
        query = query.filter(Venue.departementCode == departement_code)

    return query \
        .join(Offerer) \
        .join(UserOfferer) \
        .join(Stock, Stock.offerId == Offer.id) \
        .filter(Offer.type != str(EventType.ACTIVATION)) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .distinct(Offer.id) \
        .count()


def get_offers_available_on_discovery_count(departement_code: str = None) -> int:
    offer_ids_subquery = get_active_offers_ids_query()
    query = Offer.query.filter(Offer.id.in_(offer_ids_subquery))

    if departement_code:
        query = query.join(Venue).filter(Venue.departementCode == departement_code)

    return query.count()


def get_offers_with_non_cancelled_bookings_count(departement_code: str = None) -> int:
    query = Offer.query \
        .join(Stock) \
        .join(Booking)

    if departement_code:
        query = query.join(Venue).filter(Venue.departementCode == departement_code)

    return query \
        .filter(Booking.isCancelled == False) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .filter(Offer.type != str(EventType.ACTIVATION)) \
        .distinct(Offer.id) \
        .count()


def get_all_bookings_count(departement_code: str = None) -> int:
    return count_bookings_by_departement(departement_code) if departement_code else count_all_bookings()


def get_all_used_or_finished_bookings(departement_code: str) -> int:
    query = _query_get_used_or_finished_bookings_on_non_activation_offers() \
        .join(User)
    if departement_code:
        query = query.filter(User.departementCode == departement_code)

    return query \
        .count()


def count_all_cancelled_bookings(departement_code: str = None) -> int:
    return count_all_cancelled_bookings_by_departement(
        departement_code) if departement_code else query_count_all_cancelled_bookings()


def get_offer_counts_grouped_by_type_and_medium(query_get_counts_per_type_and_digital,
                                                counts_column_name) -> pandas.DataFrame:
    offers_by_type_and_digital_table = _get_offers_grouped_by_type_and_medium()
    offer_counts_per_type_and_digital = query_get_counts_per_type_and_digital()

    offers_by_type_and_digital_table[counts_column_name] = 0
    for offer_counts in offer_counts_per_type_and_digital:
        offer_type = offer_counts[0]
        is_digital = offer_counts[1]
        counts = offer_counts[2]
        support = 'Numérique' if is_digital else 'Physique'
        offers_by_type_and_digital_table.loc[
            (offers_by_type_and_digital_table['type'] == offer_type) & (
                    offers_by_type_and_digital_table['Support'] == support),
            counts_column_name] = counts

    offers_by_type_and_digital_table.drop('type', axis=1, inplace=True)
    offers_by_type_and_digital_table.sort_values(by=[counts_column_name, 'Catégorie', 'Support'],
                                                 ascending=[False, True, True], inplace=True)

    return offers_by_type_and_digital_table.reset_index(drop=True)


def _get_offers_grouped_by_type_and_medium() -> pandas.DataFrame:
    human_types = []
    types = []
    digital_or_physical = []

    for product_type in EventType:
        human_product_type = product_type.value['proLabel']
        human_types.append(human_product_type)
        types.append(str(product_type))
        digital_or_physical.append('Physique')

    for product_type in ThingType:
        human_product_type = product_type.value['proLabel']
        can_be_online = not product_type.value['offlineOnly']
        can_be_offline = not product_type.value['onlineOnly']

        if can_be_online:
            human_types.append(human_product_type)
            types.append(str(product_type))
            digital_or_physical.append('Numérique')

        if can_be_offline:
            human_types.append(human_product_type)
            types.append(str(product_type))
            digital_or_physical.append('Physique')

    type_and_digital_dataframe = pandas.DataFrame(
        data={'Catégorie': human_types, 'Support': digital_or_physical, 'type': types})
    type_and_digital_dataframe.sort_values(by=['Catégorie', 'Support'], inplace=True, ascending=True)
    type_and_digital_dataframe.reset_index(drop=True, inplace=True)

    return type_and_digital_dataframe


def query_get_offer_counts_grouped_by_type_and_medium() -> List[Tuple[str, bool, int]]:
    return db.engine.execute(
        """
        SELECT type, url IS NOT NULL AS is_digital, count(DISTINCT offer.id) 
        FROM offer 
        JOIN stock ON stock."offerId" = offer.id
        JOIN venue ON venue.id = offer."venueId"
        JOIN offerer ON offerer.id = venue."managingOffererId"
        JOIN user_offerer ON user_offerer."offererId" = offerer.id
        GROUP BY type, is_digital;
        """)


def query_get_offer_counts_grouped_by_type_and_medium_for_departement(departement_code: str) -> List[
    Tuple[str, bool, int]]:
    return db.engine.execute(
        text("""
        SELECT offer.type, offer.url IS NOT NULL AS is_digital, count(DISTINCT offer.id) 
        FROM offer 
        JOIN stock ON stock."offerId" = offer.id
        JOIN venue ON venue.id = offer."venueId"
        JOIN offerer ON offerer.id = venue."managingOffererId"
        JOIN user_offerer ON user_offerer."offererId" = offerer.id
        WHERE venue."departementCode"= :departementCode
         OR venue."isVirtual"
        GROUP BY type, is_digital;
        """).bindparams(departementCode=departement_code))


def query_get_booking_counts_grouped_by_type_and_medium() -> List[Tuple[str, bool, int]]:
    return db.engine.execute(
        """
        SELECT offer.type, offer.url IS NOT NULL AS is_digital, SUM(booking.quantity)
        FROM booking 
        JOIN stock ON stock.id = booking."stockId"
        JOIN offer ON offer.id = stock."offerId"
        WHERE booking."isCancelled" IS FALSE
        GROUP BY type, is_digital;
        """)


def query_get_booking_counts_grouped_by_type_and_medium_for_departement(departement_code: str) -> List[
    Tuple[str, bool, int]]:
    return db.engine.execute(
        text("""
        SELECT offer.type, offer.url IS NOT NULL AS is_digital, SUM(booking.quantity)
        FROM booking 
        JOIN stock ON stock.id = booking."stockId"
        JOIN offer ON offer.id = stock."offerId"
        JOIN "user" ON "user".id = booking."userId"
        WHERE booking."isCancelled" IS FALSE
         AND (
          "user"."departementCode"= :departementCode
          )
        GROUP BY type, is_digital;
        """).bindparams(departementCode=departement_code))
