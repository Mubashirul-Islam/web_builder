import os

from django.shortcuts import get_object_or_404
import psutil
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from website.serializers import (
    AssetSerializer,
    PageSerializer,
    WebsiteBuildSerializer,
    WebsiteSerializer,
)
from website.models import Asset, Page, Website
from website.services.asset_compression import AssetCompression
from website.services.broadcasts import Broadcast
from website.services.demo_listings import demo_listings
from website.services.website_builder import WebsiteBuilder
from website.services.asset_dimensions import AssetDimensions
from website.services.website_lock import WebsiteLock
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)


class websiteList(generics.ListCreateAPIView):
    """API endpoint that allows websites to be viewed or created."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Website.objects.prefetch_related("pages")
    serializer_class = WebsiteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "modified_at"]
    ordering = ["-modified_at"]


class websiteDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that allows a single website to be viewed, updated, or deleted."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer


class PageList(APIView):
    """API endpoint that allows pages to be viewed or created."""

    permission_classes = [IsAuthenticatedOrReadOnly]
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

    permission_classes = [IsAuthenticatedOrReadOnly]

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

    permission_classes = [IsAuthenticated]

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

    permission_classes = [IsAuthenticated]

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


class WebsiteEdit(APIView):
    """API endpoint that manages the edit lock for a specific website."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        website = get_object_or_404(Website, pk=pk)
        user_id = request.user.id

        acquired = WebsiteLock.acquire_lock(pk, user_id)

        if not acquired:
            holder = WebsiteLock.locked_by(pk)
            return Response(
                {
                    "message": "Website being edited by another user, try again later.",
                    "locked_by": holder if holder else None,
                },
                status=status.HTTP_423_LOCKED,
            )

        Broadcast.lock_acquired(pk, user_id)

        return Response(
            {
                "message": "Editing session started.",
                "website": WebsiteSerializer(website).data,
            },
            status=status.HTTP_200_OK,
        )


class WebsiteEditRefresh(APIView):
    """API endpoint that refreshes the edit lock for a specific website, extending the TTL."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        get_object_or_404(Website, pk=pk)
        user_id = request.user.id

        refreshed = WebsiteLock.refresh_lock(pk, user_id)

        if not refreshed:
            return Response(
                {
                    "message": "Editing session expired.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"message": "Editing session refreshed."}, status=status.HTTP_200_OK
        )


class WebsiteEditSave(APIView):
    """API endpoint that saves changes to a specific website and releases the edit lock."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        website = get_object_or_404(Website, pk=pk)
        user_id = request.user.id

        lock_exists, is_same_user = WebsiteLock.check_lock_for_save(pk, user_id)

        if not lock_exists:
            return Response(
                {
                    "message": "Editing session expired. Changes could not be saved.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        if not is_same_user:
            return Response(
                {
                    "message": "Editing session expired. Website being edited by another user.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # TODO: persist the changes to the database here

        WebsiteLock.release_lock(pk, user_id)
        Broadcast.lock_released(pk)

        return Response(
            {
                "message": "Changes saved successfully.",
                "website": WebsiteSerializer(website).data,
            },
            status=status.HTTP_200_OK,
        )


class WebsiteEditExit(APIView):
    """API endpoint that releases the edit lock for a specific website when the user exits the edit page without saving."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        get_object_or_404(Website, pk=pk)
        user_id = request.user.id

        WebsiteLock.release_lock(pk, user_id)  # idempotent
        Broadcast.lock_released(pk)

        return Response(
            {"message": "Editing session ended."}, status=status.HTTP_200_OK
        )


class ResourceMonitor(APIView):
    """API endpoint that provides real-time system resource usage metrics including CPU and memory usage for both the overall system and the current process."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return current system resource usage metrics including CPU and memory usage for both the overall system and the current process."""

        process = psutil.Process(os.getpid())

        return Response(
            {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "process_cpu_percent": process.cpu_percent(interval=1),
                "process_memory_mb": process.memory_info().rss / 1024 / 1024,
            },
            status=status.HTTP_200_OK,
        )
    
class DemoListings(APIView):
    """API endpoint that provides a list of demo properties."""

    permission_classes = [AllowAny]

    def get(self, request):
        '''Return a list of demo property listings with details such as title, location, price, rating, and features.'''
        return Response(
            demo_listings(),
            status=status.HTTP_200_OK,
        )
