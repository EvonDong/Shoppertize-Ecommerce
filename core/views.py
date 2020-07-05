from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView, View
from django.db.models import *
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "home-page.html", context)


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "product-page.html", context)


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"


class BestSellerView(ListView):
    model = Item
    paginate_by = 8
    template_name = "bestseller.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'account/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order! ):")
            return redirect("/")


class ProductDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


def checkout(request):
    context = {
        # 'items': Item.objects.all()
    }
    return render(request, "checkout-page.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        ordered=False,
        user=request.user
    )
    order_qs = Order.objects.filter(
        user=request.user, ordered=False)  # qs: : query set
    if order_qs.exists():
        order = order_qs[0]
        # Check if order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item's quantity is updated!")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item is now added to your cart!")
            order.items.add(order_item)
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item is now added to your cart!")
    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user, ordered=False)  # qs: : query set
    if order_qs.exists():
        order = order_qs[0]
        # Check if order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                ordered=False,
                user=request.user
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item is now removed from the cart!")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item is not in your cart!")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order!")
        return redirect("core:product", slug=slug)

    return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user, ordered=False)  # qs: : query set
    if order_qs.exists():
        order = order_qs[0]
        # Check if order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                ordered=False,
                user=request.user
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity is now updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item is not in your cart!")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order!")
        return redirect("core:product", slug=slug)

    return redirect("core:product", slug=slug)
