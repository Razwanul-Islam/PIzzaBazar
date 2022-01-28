from .models import CartItem

def cartItemNumber(request):
    if request.user.is_authenticated:
        cartItem = CartItem.objects.filter(user=request.user).count
    else:
        cartItem = 0
    return {'cartItemNumber':cartItem}
