
from .views import heatmap, articles, sentiments, narrative, chat, topic
from django.urls import path, include


urlpatterns = [
    
    # returns the narratives and their total occurence by article date
    path("api/recent/narratives", narrative.narrativeList.as_view(), name="narrative_list" ),
    # retruns the narratives and article occurence given a certain date range
    path("api/counts/narratives", narrative.narrativeCounts.as_view(), name="narrative_counts" ),
    #pk 0 for all users
    path("api/fetch/articles/<int:pk>", articles.fetchArticles.as_view(), name="fetch_articles" ),
    
    path("api/heatmap/<int:start>/<int:end>", heatmap.HeatMap.as_view(), name="heatmaps" ),
    path("api/heatmap/narrative/<int:start>/<int:end>", heatmap.NarrativeHeatMap.as_view(), name="narrative_heatmaps"),
    
    path("api/heatmap/all", heatmap.allSentimentsByArticleDate.as_view(), name="heatmaps_all" ),
    
    path("api/sentiment/range", sentiments.sentimentsByScore.as_view(), name="sentiments_by_score" ),
    path("api/trending", articles.TrendingArticles.as_view(), name="trending"),
    
    path("api/topics", topic.TopicAPIView.as_view(), name="topics"),
    
    
    path("api/chatbot", chat.DefaultChat.as_view(), name="chatbot"),
    path("api/chatbotWithCertainArticles",chat.ArticleChat.as_view(),name="chatbotWithCertainArticles"),
]
    # # signup and login with email password
    # path(
    #     "api/trending", SentimentViewSet.as_view({"get": "trending"}), name="trending"
    # ),
    # path(
    #     "api/sentiments",
    #     SentimentViewSet.as_view({"get": "sentiment_analysis_data"}),
    #     name="sentiments",
    # ),
    # path(
    #     "api/article_serch",
    #     SentimentViewSet.as_view({"post": "article_serch"}),
    #     name="article_serch",
    # ),
    # path(
    #     "api/sentiment_percentage_serch",
    #     SentimentViewSet.as_view({"post": "sentiment_percentage_serch"}),
    #     name="sentiment_percentage_serch",
    # ),
    # path(
    #     "api/user_dashboard_sentiments",
    #     SentimentViewSet.as_view({"get": "user_dashboard_sentiments"}),
    #     name="user_dashboard_sentiments",
    # ),
    # path(
    #     "api/sentiment_graph",
    #     SentimentViewSet.as_view({"get": "sentiment_graph"}),
    #     name="sentiment_graph",
    # ),
    # path(
    #     "api/all_sentiment_percentages",
    #     SentimentViewSet.as_view({"get": "all_sentiment_percentages"}),
    #     name="all_sentiment_percentages",
    # ),
    # path(
    #     "api/pos_neg_ratios",
    #     SentimentViewSet.as_view({"get": "pos_neg_ratios"}),
    #     name="pos_neg_ratios",
    # ),
    # path(
    #     "api/sentiment_filter",
    #     SentimentViewSet.as_view({"post": "sentiment_filter"}),
    #     name="sentiment_filter",
    # ),
    # path(
    #     "api/all_flagged",
    #     SentimentViewSet.as_view({"get": "all_flagged"}),
    #     name="all_flagged",
    # ),
    # path(
    #     "api/mention_week",
    #     SentimentViewSet.as_view({"get": "mention_week"}),
    #     name="mention_week",
    # ),
    # path("api/chatbot", SentimentViewSet.as_view({"post": "chatbot"}), name="chatbot"),
    # path(
    #     "api/chatbotWithCertainArticles",
    #     SentimentViewSet.as_view({"post": "chatbotWithCertainArticles"}),
    #     name="chatbotWithCertainArticles",
    # ),

