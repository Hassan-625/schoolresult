<?php
use App\Http\Controllers\AuthController;use App\Http\Controllers\DashboardController;use App\Http\Controllers\PlatformController;use App\Http\Controllers\ResultController;use App\Http\Controllers\SubscriptionController;use Illuminate\Support\Facades\Route;
Route::view('/','welcome')->name('home');Route::get('/login',[AuthController::class,'show'])->name('login');Route::post('/login',[AuthController::class,'login'])->name('login.attempt');Route::post('/logout',[AuthController::class,'logout'])->name('logout');
Route::middleware(['auth','school'])->group(function(){
 Route::get('/dashboard',DashboardController::class)->name('dashboard');
 Route::get('/results',[ResultController::class,'index'])->middleware('permission:academics.read')->name('results.index');
 Route::post('/results',[ResultController::class,'store'])->middleware('permission:academics.write')->name('results.store');
 Route::get('/subscription',[SubscriptionController::class,'show'])->middleware('permission:subscription.manage')->name('subscription.show');
 Route::post('/subscription/offline',[SubscriptionController::class,'offline'])->middleware('permission:subscription.manage')->name('subscription.offline');
});
Route::middleware(['auth','superadmin'])->prefix('platform')->group(function(){Route::get('/',[PlatformController::class,'index'])->name('platform');Route::post('/schools/{school}',[PlatformController::class,'update'])->name('platform.schools.update');Route::post('/upgrades/{upgrade}/approve',[PlatformController::class,'approve'])->name('platform.upgrades.approve');});
Route::post('/webhooks/paystack',[SubscriptionController::class,'paystack'])->name('webhooks.paystack');Route::post('/webhooks/flutterwave',[SubscriptionController::class,'flutterwave'])->name('webhooks.flutterwave');
