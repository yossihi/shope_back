"""
apppppppppppppppplication urls
"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import APIViews, MyTokenObtainPairView, buyProd, calcTotal, checkOut, create, get_cart, getImages, products, unBuy

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view()),
    path('register/', create),
    path('products/', products),
    path('products/<int:id>', products),
    path('buyProd/<int:id>', buyProd),
    path('getCart/', get_cart),
    path('unbuy/<int:id>', unBuy),
    path('get_all_images', getImages),
    path('upload_image/', APIViews.as_view()),
    path('checkOut/', checkOut),
    path('calcTotal/', calcTotal)

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
