import hashlib, hmac, json
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import School, SubscriptionPayment

@transaction.atomic
def apply_successful_payment(provider,reference,school_id,target_tier,amount,payload):
    payment,created=SubscriptionPayment.objects.select_for_update().get_or_create(reference=reference,defaults={"provider":provider,"school_id":school_id,"target_tier":target_tier,"amount":amount,"metadata":payload})
    if payment.status=="success": return payment
    payment.status="success"; payment.paid_at=timezone.now(); payment.metadata=payload; payment.save()
    school=School.objects.select_for_update().get(pk=school_id); school.tier=target_tier; school.subscription_status=School.ACTIVE
    base=max(timezone.now(),school.subscription_expires_at or timezone.now()); school.subscription_expires_at=base+timedelta(days=365); school.save()
    return payment

def valid_paystack(body,signature): return bool(settings.PAYSTACK_SECRET_KEY) and hmac.compare_digest(hmac.new(settings.PAYSTACK_SECRET_KEY.encode(),body,hashlib.sha512).hexdigest(),signature or "")
def valid_flutterwave(signature): return bool(settings.FLUTTERWAVE_WEBHOOK_HASH) and hmac.compare_digest(settings.FLUTTERWAVE_WEBHOOK_HASH,signature or "")
