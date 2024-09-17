from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.conf import settings
from base.models import Item, Order
import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
import json
from django.contrib import messages

stripe.api_key = settings.STRIPE_API_SECRET_KEY

tax_rate = stripe.TaxRate.create(
    display_name="Tax",
    description="Tax",
    country="AU",
    jurisdiction="AU", 
    percentage=settings.TAX_RATE * 100,  # 10%
    inclusive=False, # without tax
)


class PaySuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/success.html'

    def get(self, request, *args, **kwargs):
        # query from checkout_session
        order_id = request.GET.get('order_id')

        # Order object list referring to id and current user
        orders = Order.objects.filter(user=request.user, id=order_id)

        if len(orders) != 1:
            return super().get(request, *args, **kwargs)

        order = orders[0]


        if order.is_confirmed:
            return super().get(request, *args, **kwargs)

        order.is_confirmed = True  # order confirmed
        order.save()

        # Delete cart info
        if 'cart' in request.session:
            del request.session['cart']

        return super().get(request, *args, **kwargs)


class PayCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/cancel.html'

    def get(self, request, *args, **kwargs):
        # tentative orders from current user
        orders = Order.objects.filter(user=request.user, is_confirmed=False)

        for order in orders:
            # reverse stock and sold_count
            for elem in json.loads(order.items):
                item = Item.objects.get(pk=elem['pk'])
                item.sold_count -= elem['quantity']
                item.stock += elem['quantity']
                item.save()
        orders.delete()

        return super().get(request, *args, **kwargs)



def create_line_item(unit_amount, name, quantity):
    return {
        'price_data': {
            'currency': 'aud',
            'unit_amount': unit_amount * 100,
            'product_data': {'name': name, },
        },
        'quantity': quantity,
        "tax_rates": [tax_rate.id],
    }

def check_profile_filled(profile):
    if profile.name is None or profile.name == '':
        return False
    elif profile.zipcode is None or profile.zipcode == '':
        return False
    elif profile.prefecture is None or profile.prefecture == '':
        return False
    elif profile.city is None or profile.city == '':
        return False
    elif profile.address1 is None or profile.address1 == '':
        return False
    return True


class PayWithStripe(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        # if the profile is not filled
        if not check_profile_filled(request.user.profile):
            messages.error(self.request, 'Please complete your profile for delivery.')
            return redirect('/profile/')

        cart = request.session.get('cart', None)
        if cart is None or len(cart) == 0:
            messages.error(self.request, 'Your cart is empty')
            return redirect('/')

        items = []
        line_items = []
        for item_pk, quantity in cart['items'].items():
            item = Item.objects.get(pk=item_pk)
            line_item = create_line_item(
                item.price, item.name, quantity)
            line_items.append(line_item)
        
            # set up for order models
            items.append({
                "pk": item.pk,
                "name": item.name,
                "image": str(item.image),
                "price": item.price,
                "quantity": quantity,
            })

            item.stock -= quantity
            item.sold_count += quantity
            item.save()

        # create order details before check out
        order = Order.objects.create(
            user=request.user,
            uid=request.user.pk,
            items=json.dumps(items),
            shipping=serializers.serialize("json", [request.user.profile]),
            amount=cart['total'],
            tax_included=cart['tax_included_total']
        )

        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'{settings.MY_URL}/pay/success/?order_id={order.pk}',
            cancel_url=f'{settings.MY_URL}/pay/cancel/',
        )
        return redirect(checkout_session.url)