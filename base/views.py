from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import serializers
from .models import Order, Order_Detail, Product
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_admin'] = user.is_superuser
        token['username'] = user.username
 
        return token
 
 
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    
    def create(self, validated_data):
        return Product.objects.create(**validated_data)
    def update(self, instance, validate_data):
        instance.price = validate_data.get('price', instance.price)
        instance.desc = validate_data.get('desc', instance.desc)
        instance.img = validate_data.get('img', instance.img) 
        instance.save()
        return instance
    

class APIViews(APIView):
    parser_class=(MultiPartParser,FormParser)
    def post(self,request,*args,**kwargs):
        api_serializer=ProductSerializer(data=request.data)
        if api_serializer.is_valid():
            api_serializer.save()
            return Response(api_serializer.data,status=status.HTTP_201_CREATED)
        else:
            print('error',api_serializer.errors)
            return Response(api_serializer.errors,status=status.HTTP_400_BAD_REQUEST)



    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
    def create(self, validated_data):
        return Order.objects.create(**validated_data)
    
class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order_Detail
        fields = '__all__'
    def create(self, validated_data):
        return Order_Detail.objects.create(**validated_data)
    

@api_view(['POST'])
def create(request):
        User.objects.create_user(username= request.data["username"],password=request.data['password'],is_staff=1)
        return Response({"reg":"test"})


@api_view(['GET','POST','DELETE','PUT','PATCH'])
@permission_classes([IsAuthenticated])
def products(req,id=-1):
    if req.method =='GET':
        if id > -1:
            try:
                temp_prod=Product.objects.get(id=id)
                return Response (ProductSerializer(temp_prod,many=False).data)
            except Product.DoesNotExist:
                return Response ("not found")
        all_prods=ProductSerializer(Product.objects.all(),many=True).data
        return Response (all_prods)
    if req.method == 'POST':
        print(req.data)
        prod_serializer = ProductSerializer(data=req.data)
        if prod_serializer.is_valid():
            prod_serializer.save()
            return Response("post...")
        else:
            return Response(prod_serializer.errors)
    if req.method =='DELETE':
        try:
            temp_prod=Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response ("not found")    
       
        temp_prod.delete()
        return Response ("del...")
    if req.method =='PUT':
        try:
            temp_prod=Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response ("not found")
        
        ser = ProductSerializer(data=req.data)
        old_task = Product.objects.get(id=id)
        ser.update(old_task, req.data)
        return Response('updated')
    
@api_view(['post'])
@permission_classes([IsAuthenticated])
def buyProd(req, id):
    try:
        order_instance = Order.objects.get(customer=req.user.id, completed= False)
    except Order.DoesNotExist:
        order_serializer = OrderSerializer(data={'customer': req.user.id})
        if order_serializer.is_valid():
            order_instance = order_serializer.save()
        else:
            return Response(order_serializer.errors)

    try:
        product_instance = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response("Product not found")

    try:
        order_detail_instance = Order_Detail.objects.get(order_id=order_instance.id, product_id=product_instance.id)
        order_detail_instance.amount += 1
        order_detail_instance.save()
        return Response('Product amount updated in the order')
    except Order_Detail.DoesNotExist:
        new_order_detail_serializer = OrderDetailSerializer(data={"order": order_instance.id, "product": product_instance.id})
        if new_order_detail_serializer.is_valid():
            new_order_detail_serializer.save()
            return Response('Product added to the order')
        else:
            return Response(new_order_detail_serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(req):
    try:
        order_instance = Order.objects.get(customer=req.user.id, completed=False)
    except Order.DoesNotExist:
        return Response([])
    order_details = Order_Detail.objects.filter(order_id=order_instance)
    order_details_serializer = OrderDetailSerializer(order_details, many=True)
    display_order = []
    for order_prod in order_details_serializer.data:
        prod = Product.objects.get(id=order_prod['product'])
        display_order.append(
            {
                "desc": prod.desc,
                "price": prod.price,
                "quantity": order_prod['amount'],
                "id": order_prod["id"]
            }
        )
    print(display_order)
    return Response(display_order)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unBuy(req, id):
    try:
        temp_prod=Order_Detail.objects.get(id=id)
        if int(temp_prod.amount) > 1:
            temp_prod.amount -= 1
            temp_prod.save()
        else:
            Order_Detail.delete(temp_prod)
    except Order.DoesNotExist:
        return Response ("not found")
    return Response('unbuyed')


@api_view(['GET'])
def getImages(request):
    res=[]
    for img in Product.objects.all():
        res.append({"title":img.title,
                "description":img.description,
                "completed":False,
               "image":str( img.image)
                }) 
    return Response(res)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def checkOut(req):
    order_temp = Order.objects.get(customer=req.user.id, completed=False)
    order_temp.completed = True
    order_temp.save()
    return Response('Completed...')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calcTotal(req):
    total = 0
    try:
        order_instance = Order.objects.get(customer=req.user.id, completed=False)
    except Order.DoesNotExist:
        print(total)
        return Response({"total": total})
    order_details = Order_Detail.objects.filter(order_id=order_instance)
    order_details_serializer = OrderDetailSerializer(order_details, many=True)
    if len(order_details_serializer.data) != 0:
        for prod in order_details_serializer.data:
            cur_prod = Product.objects.get(id=prod['product'])
            total += cur_prod.price * prod['amount']
    print(total)
    return Response({"total": total})