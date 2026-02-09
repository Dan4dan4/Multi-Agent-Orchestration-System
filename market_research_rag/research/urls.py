from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, query_rag
from .views import ask_rag, upload_document, clear_docs

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('query/', query_rag, name='query-rag'),
    path("ask/", ask_rag),
    path('upload/', upload_document, name='upload-document'),
    path('clear_docs/', clear_docs, name='clear-documents'),
]
