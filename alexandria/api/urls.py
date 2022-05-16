from rest_framework.routers import DefaultRouter

from alexandria.api import views

router = DefaultRouter()
router.register(r"items", views.ItemViewSet, basename="items")
router.register(r"holds", views.HoldViewSet, basename="holds")
router.register(r"records", views.RecordViewSet, basename="records")
router.register(r"checkouts", views.CheckoutViewSet, basename="checkouts")
urlpatterns = router.urls
