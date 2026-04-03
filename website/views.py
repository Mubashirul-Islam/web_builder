from functools import cache

from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from website.serializers import (
    AssetSerializer,
    LockStatusSerializer,
    PageSerializer,
    WebsiteBuildSerializer,
    WebsiteSerializer,
)
from website.models import Asset, Page, Website
from website.services.asset_compression import AssetCompression
from website.services.build_website import WebsiteBuilder
from website.services.asset_dimensions import AssetDimensions


class websiteList(generics.ListCreateAPIView):
    """API endpoint that allows websites to be viewed or created."""

    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "modified_at"]
    ordering = ["-modified_at"]


class websiteDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that allows a single website to be viewed, updated, or deleted."""

    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer


class PageList(APIView):
    """API endpoint that allows pages to be viewed or created."""

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_at", "modified_at"]
    ordering = ["-modified_at"]

    def get_queryset(self):
        """Return the base queryset for listing pages."""
        return Page.objects.all()

    def filter_queryset(self, queryset):
        """Apply configured filter backends to the provided queryset."""
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_paginator(self):
        """Instantiate the default paginator when pagination is enabled."""
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        if not pagination_class:
            return None
        return pagination_class()

    def get(self, request):
        """List pages with optional filtering, ordering, and pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.get_paginator()

        if paginator is not None:
            page = paginator.paginate_queryset(queryset, request, view=self)
            if page is not None:
                serializer = PageSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

        serializer = PageSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new page from the request payload."""
        serializer = PageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PageDetail(APIView):
    """API endpoint that allows a single page to be viewed, updated, or deleted."""

    def get_object(self, pk):
        """Return a page by primary key or raise 404 if it does not exist."""
        return get_object_or_404(Page, pk=pk)

    def get(self, request, pk):
        """Retrieve a single page by primary key."""
        page = self.get_object(pk)
        serializer = PageSerializer(page)
        return Response(serializer.data)

    def put(self, request, pk):
        """Fully update an existing page by primary key."""
        page = self.get_object(pk)
        serializer = PageSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partially update an existing page by primary key."""
        page = self.get_object(pk)
        serializer = PageSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete an existing page by primary key."""
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WebsiteBuild(APIView):
    """API endpoint that triggers the build process for a specific website."""

    def post(self, request, pk):
        """Trigger the build process for the specified website."""
        website = get_object_or_404(Website, pk=pk)
        serializer = WebsiteBuildSerializer(
            website,
            data=request.query_params,
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        mode = serializer.validated_data["mode"]

        try:
            WebsiteBuilder.build_website(website, mode)
        except Exception:
            return Response(
                {"error": "Build process failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": f"Build process triggered for website '{website.name}' in {mode} mode."
            },
            status=status.HTTP_200_OK,
        )


class AssetUpload(APIView):
    """API endpoint that allows assets to be uploaded to a specific website."""

    def post(self, request, pk):
        """Handle file uploads for a specific website identified by primary key."""
        website = get_object_or_404(Website, pk=pk)

        serializer = AssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        counters = {
            Asset.AssetType.IMAGE: 0,
            Asset.AssetType.VIDEO: 0,
        }

        for file_obj, file_type, alt_text in serializer.validated_data:
            compressed_file = AssetCompression.compress(file_obj, file_type)
            width, height = AssetDimensions.get_dimensions(compressed_file, file_type)
            counters[file_type] += 1

            Asset.objects.create(
                website=website,
                file=compressed_file,
                type=file_type,
                size=compressed_file.size,
                alt_text=alt_text,
                height=height,
                width=width,
            )

        return Response(
            {
                "message": "Assets uploaded successfully.",
                "images": counters[Asset.AssetType.IMAGE],
                "videos": counters[Asset.AssetType.VIDEO],
            },
            status=status.HTTP_201_CREATED,
        )

class WebsiteEditView(APIView):
    """
    Attempt to acquire the edit lock for `pk`.
 
    Flow:
      1. Check whether website_pk is in Redis.
      2a. Key absent  (False) → store lock, return edit data, broadcast "lock acquired".
      2b. Key present (True)  → check same user?
            Same user  → refresh TTL, return edit data (re-entry / page refresh).
            Other user → 423 Locked.
    """

    def get(self, request, pk):
        website = get_object_or_404(Website, pk=pk)
        user_id = 1 
        #request.user.id
 
        acquired = acquire_lock(pk, user_id)
 
        if not acquired:
            holder = get_lock(pk)
            data = LockStatusSerializer(
                {
                    "status": "locked",
                    "message": "Website being edited by another user, try again later.",
                    "locked_by": holder.get("user_id") if holder else None,
                }
            ).data
            return Response(data, status=status.HTTP_423_LOCKED)
 
        #broadcast_lock_acquired(pk, user_id)

        LOCK_KEY_PREFIX = "website_lock"
        LOCK_TTL_SECONDS = 5 * 60  # 5 minutes

        def get_lock(website_pk: int) -> dict | None:
            """
            Return the lock data dict {"user_id": ..., "ttl": ...} if the lock exists,
            or None if there is no active lock.
            """
            return cache.get(_lock_key(website_pk))
        
        def acquire_lock(website_pk: int, user_id: int) -> bool:
            """
            Attempt to atomically acquire the lock for `website_pk`.
            Uses add() which only sets the key if it does NOT already exist.
            Returns True if the lock was acquired, False if already held by someone else.
            If already held by the SAME user, refreshes TTL and returns True.
            """
            key = _lock_key(website_pk)
            lock_data = {"user_id": user_id}
        
            # add() is atomic: sets only if key absent (NX behaviour)
            acquired = cache.add(key, lock_data, timeout=LOCK_TTL_SECONDS)
            if acquired:

                return True
        
            # Key already exists — check if it belongs to this user
            existing = cache.get(key)
            if existing and existing.get("user_id") == user_id:
                # Same user re-entering (e.g. page refresh) — refresh TTL
                cache.set(key, lock_data, timeout=LOCK_TTL_SECONDS)
                return True
        
            return False
        
        def _lock_key(website_pk: int) -> str:
            return f"{LOCK_KEY_PREFIX}:{website_pk}"
 
        return Response(
            {
                "status": "ok",
                "website": WebsiteSerializer(website).data,
            }
        )
        