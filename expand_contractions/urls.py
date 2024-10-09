from django.urls import path
from .views import ExpandContractionsAPIView

urlpatterns = [
    path('api/expand-contractions/', ExpandContractionsAPIView.as_view(), name='expand_contractions'),
]
