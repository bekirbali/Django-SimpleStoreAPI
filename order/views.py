from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from product.models import Product

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        # Get the current cart
        user = self.get_or_create_default_user()
        cart_order = Order.objects.filter(user=user, status='cart').first()
        
        if not cart_order:
            return Response(
                {'error': 'No active cart found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update order with shipping information
        shipping_fields = [
            'full_name', 'email', 'phone', 'address', 
            'city', 'postal_code', 'notes'
        ]
        
        for field in shipping_fields:
            if field in request.data:
                setattr(cart_order, field, request.data[field])
        
        # Change status to pending
        cart_order.status = 'pending'
        cart_order.save()
        
        serializer = self.get_serializer(cart_order)
        return Response(serializer.data)

    def get_or_create_default_user(self):
        user, created = User.objects.get_or_create(
            username='anonymous',
            defaults={'email': 'anonymous@example.com'}
        )
        return user

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny]
    
    def get_or_create_default_user(self):
        user, created = User.objects.get_or_create(
            username='anonymous',
            defaults={'email': 'anonymous@example.com'}
        )
        return user
    
    def get_queryset(self):
        user = self.get_or_create_default_user()
        cart_order = Order.objects.filter(user=user, status='cart').first()
        if cart_order:
            return OrderItem.objects.filter(order=cart_order)
        return OrderItem.objects.none()
    
    def create(self, request):
        user = self.get_or_create_default_user()
        cart_order = Order.objects.filter(user=user, status='cart').first()
        if not cart_order:
            cart_order = Order.objects.create(user=user, status='cart')
        
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        order_item, created = OrderItem.objects.get_or_create(
            order=cart_order,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            order_item.quantity = quantity
            order_item.save()
            
        serializer = self.get_serializer(order_item)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        try:
            user = self.get_or_create_default_user()
            cart_order = Order.objects.filter(user=user, status='cart').first()
            
            if not cart_order:
                return Response(
                    {'error': 'No active cart found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            order_item = OrderItem.objects.filter(
                order=cart_order,
                product_id=pk
            ).first()
            
            if not order_item:
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            quantity = request.data.get('quantity', 1)
            order_item.quantity = quantity
            order_item.save()
            
            serializer = self.get_serializer(order_item)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, pk=None):
        try:
            user = self.get_or_create_default_user()
            cart_order = Order.objects.filter(user=user, status='cart').first()
            if not cart_order:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            order_item = OrderItem.objects.filter(order=cart_order, product_id=pk).first()
            if not order_item:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            order_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        user = self.get_or_create_default_user()
        cart_order = Order.objects.filter(user=user, status='cart').first()
        if cart_order:
            cart_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
