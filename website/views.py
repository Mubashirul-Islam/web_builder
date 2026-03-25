from django.shortcuts import get_object_or_404
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
from website.services.build_website import build_website
from website.utils.image_dimensions import get_image_dimensions
from website.utils.video_dimensions import get_video_dimensions


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
            build_website(website, mode)
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

        image_count = 0
        video_count = 0

        for file_obj, file_type, alt_text in serializer.validated_data:
            
            if file_type == Asset.AssetType.IMAGE:
                h, w = get_image_dimensions(file_obj)
                image_count += 1
                
            elif file_type == Asset.AssetType.VIDEO:
                h, w = get_video_dimensions(file_obj)
                video_count += 1

            Asset.objects.create(
                website=website,
                file=file_obj,
                type=file_type,
                size=file_obj.size,
                alt_text=alt_text,
                height=h,
                width=w

            )

        return Response(
            {
                "message": "Assets uploaded successfully.",
                "images": image_count,
                "videos": video_count,
            },
            status=status.HTTP_201_CREATED,
        )
