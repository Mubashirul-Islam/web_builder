from rest_framework import generics, filters
from website.serializers import PageSerializer, WebsiteSerializer
from website.models import Page, Website


class websiteList(generics.ListCreateAPIView):
    '''API endpoint that allows websites to be viewed or created.'''
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']    
    ordering_fields = ['created_at', 'modified_at']
    ordering = ['-modified_at']

class websiteDetail(generics.RetrieveUpdateDestroyAPIView):
    '''API endpoint that allows a single website to be viewed, updated, or deleted.'''
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

class PageList(generics.ListCreateAPIView):
    '''API endpoint that allows pages to be viewed or created.'''
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at', 'modified_at']
    ordering = ['-modified_at']

class PageDetail(generics.RetrieveUpdateDestroyAPIView):
    '''API endpoint that allows a single page to be viewed, updated, or deleted.'''
    queryset = Page.objects.all()
    serializer_class = PageSerializer