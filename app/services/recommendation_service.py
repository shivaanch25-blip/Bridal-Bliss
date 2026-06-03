from app.utils.ai_engine import get_hybrid_product_recommendations, get_recommended_salons


class RecommendationService:
    @staticmethod
    def get_products(user_pref=None, look=None, limit=4):
        return get_hybrid_product_recommendations(user_pref=user_pref, look=look, limit=limit)

    @staticmethod
    def get_salons(latitude, longitude, look=None, limit=3):
        return get_recommended_salons(latitude, longitude, look=look, limit=limit)
