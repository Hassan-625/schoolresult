<?php
return ['paystack'=>['secret'=>env('PAYSTACK_SECRET_KEY'),'public'=>env('PAYSTACK_PUBLIC_KEY')],'flutterwave'=>['secret'=>env('FLUTTERWAVE_SECRET_KEY'),'webhook_hash'=>env('FLUTTERWAVE_WEBHOOK_HASH')],'google'=>['client_id'=>env('GOOGLE_CLIENT_ID'),'client_secret'=>env('GOOGLE_CLIENT_SECRET'),'redirect'=>env('GOOGLE_REDIRECT_URI')]];
