from models import PcObject
from repository.offer_queries import find_offers_by_venue_id
from repository.venue_queries import find_by_id
from utils.human_ids import dehumanize


def delete_venue_and_offers_for_venue_id(humanized_venue_id: str):
    dehumanized_venue_id = dehumanize(humanized_venue_id)
    offers = find_offers_by_venue_id(dehumanized_venue_id)
    venue = find_by_id(dehumanized_venue_id)

    if any([offer.stocks for offer in offers]):
        raise AttributeError('Offres non supprimables car au moins une contient des stocks')

    for offer in offers:
        PcObject.delete(offer)

    if venue:
        PcObject.delete(venue)
