from typing import List
from models import Favorite, Mediation, Offer, User


def create_favorite(mediation: Mediation, offer: Offer, user: User) -> Favorite:
    favorite = Favorite()
    favorite.mediation = mediation
    favorite.offer = offer
    favorite.user = user
    return favorite

def find_matching_recommendations_from_favorite(favorite: Favorite, user: User) -> List:
    matching_recommendations = []
    recommendations = [
        recommendation
        for recommendation in favorite.offer.recommendations
        if recommendation.userId == user.id
    ]
    if favorite.mediationId:
        return [
            recommendation
            for recommendation in recommendations
            if recommendation.mediationId == favorite.mediationId
        ]
    return [recommendations[0]]
