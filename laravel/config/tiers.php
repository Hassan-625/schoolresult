<?php
return [
    'small'=>['label'=>'Small','student_limit'=>150,'price'=>(int) env('SMALL_TIER_PRICE',15000),'features'=>['student_profiles','terminal_results']],
    'mid'=>['label'=>'Mid-Tier','student_limit'=>500,'price'=>(int) env('MID_TIER_PRICE',35000),'features'=>['student_profiles','terminal_results','broadsheets','sms','fees']],
    'premium'=>['label'=>'Premium','student_limit'=>null,'price'=>(int) env('PREMIUM_TIER_PRICE',75000),'features'=>['student_profiles','terminal_results','broadsheets','sms','fees','cbt','payroll','expenses','online_fees']],
];
