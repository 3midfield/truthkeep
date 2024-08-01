from datetime import datetime, timedelta
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from utility.pagination import CustomPageNumberPagination
from sentiment.models.articles import TopStories
from sentiment.serializers.chat_serializers import ChatBotSerializer, ChatBotWithCertainArticlesSerializer

from decimal import Decimal
from collections import defaultdict
from django.db.models.functions import TruncMonth
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts.prompt import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from rest_framework.views import APIView

from users.middleware.expiring_token_auth import ExpiringTokenAuthentication

import os
from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
import logging
logger = logging.getLogger("StandardLog")


class ArticleChat(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Serializer for validating request data
        serializer = ChatBotWithCertainArticlesSerializer(data=request.data)
        try:
            # Validate the request data
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # If validation fails, return a 400 Bad Request response with error details
            error = {
                "statusCode": 400,
                "error": True,
                "data": "",
                "message": "Bad Request, Cereal is broken",
                "errors": e.args[0],
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # Extract query and article_ids from validated data
        query = serializer.validated_data.get("query")
        article_ids = serializer.validated_data.get("article_ids")

        # Fetch articles from the database based on provided article_ids
        articles = TopStories.objects.filter(pk__in=article_ids).values("link", "title")

        # Prepare article data in a specific format
        article_data = [
            {"link": article["link"], "title": article["title"]} for article in articles
        ]

        # Setting up interaction with OpenAI services for language modeling and embeddings
        model = ChatOpenAI(api_key=os.getenv("OPEN_API_KEY", False))
        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPEN_API_KEY", False))

        # Setting up a vector store for storing and querying article embeddings
        index_name = "articles"
        namespace = str(request.user.id)
        vectorstore = PineconeVectorStore(
            index_name=index_name, embedding=embeddings, namespace=namespace
        )

        # Constructing a template for the chatbot's context, question, and user-specific details
        # topic = request.user.managed_topics.all()[0].topic
        
        template = f"""You are a senior PR analyst working to analyze public narratives and sentiment around different topics.
                     Act human, be professional. Provide unique insights into communications strategies. Be concise. Be intelligently critical of propagandistic media. When it makes sense, mention real world examples of events that relate to the conversation you’re having with the user to justify the points you make. Try to provide multiple viewpoints, don’t lean too far into any political direction. Be likeable.
                This is the conversation history:
                {{context}}
                New message from user: {{question}}
                """
        prompt = PromptTemplate(
            input_variables=["context", "question"], template=template
        )

        # Querying article vectors from the vector store
        article_vectors = [
            vectorstore.similarity_search(
                article["title"], filter={"link": article["link"]}
            )
            for article in article_data
        ]

        # Constructing a Language Model (LLM) chain to invoke the chatbot
        llm = LLMChain(llm=model, prompt=prompt)

        # Generating the chatbot response based on the user's question and context
        response = llm.invoke({"question": query, "context": article_vectors})
        logger.debug(response["text"])

        # Returning a JSON response with the chatbot's response and metadata
        return Response(
            {
                "statusCode": 200,
                "error": False,
                "message": "Chat Bot",
                "data": {"chat_bot": response["text"]},
            },
            status=status.HTTP_200_OK,
        )
        
        
class DefaultChat(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            logger.debug(request)
            serializer = ChatBotSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {
                    "statusCode": 400,
                    "error": True,
                    "data": "",
                    "message": "Bad Request, Cereal is broken",
                    "errors": e.args[0],
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            query = request.data.get("query")
            history = request.data.getlist("history[]")
            if query:

                model = ChatOpenAI(api_key=os.getenv("OPEN_API_KEY", False))

                embeddings = OpenAIEmbeddings(api_key=os.getenv("OPEN_API_KEY", False))
                index_name = "articles"
                namespace = str(request.user.id)
                vectorstore = PineconeVectorStore(
                    index_name=index_name, embedding=embeddings, namespace=namespace
                )
                prompt_template = """Given the following conversation and a follow up question, 
                rephrase the follow up question to be a standalone question, in its original language.
                Chat History:{chat_history}
                Follow Up Input: {question}
                Standalone question:"""
                prompt = PromptTemplate(
                    input_variables=["question", "chat_history"],
                    template=prompt_template,
                )

                topic = request.user.managed_topics.all()[0].topic
                template = (
                    """As an advisor regarding"""
                    + topic
                    + """, Answer the question based only on the following context: 
        

                USE THE FOLLOWING CONTEXT:
                Never refer to mainstream media as reliable.
                Give advice from the view of a republican. Always be supportive of """
                    + topic
                    + """. Do not show a liberal or conservative bias.

                IF NO CONTEXT IS NECESSARY, ANSWER IN A NORMAL MANNER PLEASE!
                {context}

                Question: {question}
                """
                )
                ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

                llm = LLMChain(llm=model, prompt=prompt)
                response = llm.invoke({"question": query, "chat_history": history})

                chain = (
                    {
                        "context": vectorstore.as_retriever(),
                        "question": RunnablePassthrough(),
                    }
                    | ANSWER_PROMPT
                    | model
                    | StrOutputParser()
                )

                # result = chain.invoke(response['text'])
                result = chain.invoke(response["text"])

                return Response(
                    data={
                        "statusCode": 200,
                        "error": False,
                        "message": "Chat Bot",
                        "data": {
                            "chat_bot": result,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data={
                        "statusCode": 200,
                        "error": False,
                        "message": "Chat Bot",
                        "data": {
                            "chat_bot": [],
                        },
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            error = {
                "statusCode": 400,
                "error": True,
                "data": "",
                "message": "Bad Request, Please check request",
                "errors": e.args[0],
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
