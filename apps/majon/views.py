import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View


from .models import Room, Rule
from .cache import cache_room_list, get_cached_room_list


class RoomCreateView(LoginRequiredMixin, View):
    template_name = "majon/room_form.html"

    def get(self, request):
        return render(request, self.template_name, {"rules": Rule.objects.all()})

    def post(self, request):
        
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        selected_rule_ids = request.POST.getlist("rules")

        context = {
            "rules": Rule.objects.all(),
            "name": name,
            "code": code,
            "selected_rule_ids": selected_rule_ids,
        }

        if not name or not code:
            context["error"] = "請填寫房間名稱與房間代碼。"
            return render(request, self.template_name, context, status=400)

        if Room.objects.filter(code=code).exists():
            context["error"] = "這個房間代碼已被使用，請改用其他代碼。"
            return render(request, self.template_name, context, status=400)

        room = Room.objects.create(
            name=name,
            code=code,
            owner=request.user,
        )

        room.rules.set(Rule.objects.filter(id__in=selected_rule_ids))

        return redirect("majon:room-detail", room_id=room.id)



class RoomDetailView(View):
    def get(self, request, room_id):
        room = get_object_or_404(
            Room.objects.select_related("owner", "line_group").prefetch_related(
                "games",
                "rules",
            ),
            id=room_id,
        )
        return render(request, "majon/room_detail.html", {"room": room})

class RoomListView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "majon/room_list.html")


class JsonLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse(
            {"error": "authentication_required"},
            status=401,
        )


class RoomListDataView(JsonLoginRequiredMixin, View):
    page_size = 10

    def get(self, request):
        keyword = request.GET.get("q", "").strip()
        try:
            requested_page = int(request.GET.get("page", "1"))
        except (TypeError, ValueError):
            requested_page = 1
        if requested_page < 1:
            requested_page = 1

        cached_payload = get_cached_room_list(request.user.id, keyword, requested_page)
        if cached_payload is not None:
            return JsonResponse(cached_payload)

        rooms = Room.objects.select_related("owner", "owner__profile").filter(
            owner=request.user
        )

        if keyword:
            rooms = rooms.filter(name__icontains=keyword)

        paginator = Paginator(rooms, self.page_size)
        page = paginator.get_page(requested_page)

        payload = {
                "items": [
                    {
                        "id": room.id,
                        "name": room.name,
                        "code": room.code,
                        "owner_display_name": self.owner_display_name(room),
                        "detail_url": reverse(
                            "majon:room-detail", kwargs={"room_id": room.id}
                        ),
                    }
                    for room in page.object_list
                ],
                "page": page.number,
                "page_size": self.page_size,
                "total_count": paginator.count,
                "total_pages": paginator.num_pages,
                "has_previous": page.has_previous(),
                "has_next": page.has_next(),
        }
        cache_room_list(request.user.id, keyword, requested_page, payload)
        return JsonResponse(payload)

    @staticmethod
    def owner_display_name(room):
        profile = getattr(room.owner, "profile", None)
        return profile.display_name if profile and profile.display_name else room.owner.username

