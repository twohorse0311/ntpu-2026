from django.urls import path

from .views import RoomCreateView, RoomDetailView, RoomListDataView, RoomListView

app_name = "majon"

urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="room-list"),
    path("rooms/data/", RoomListDataView.as_view(), name="room-list-data"),
    path("rooms/create/", RoomCreateView.as_view(), name="room-create"),
    path("rooms/<int:room_id>/", RoomDetailView.as_view(), name="room-detail"),
]
