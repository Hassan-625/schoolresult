<?php
namespace App\Http\Controllers;use App\Models\OfflineUpgradeRequest;use App\Services\Tenant;use Illuminate\Http\Request;use Illuminate\Http\Response;use Illuminate\View\View;
class SubscriptionController {
 public function show():View{$school=Tenant::current();return view('subscription',compact('school')+['plans'=>config('tiers'),'usage'=>$school->students()->count()]);}
 public function offline(Request $request){$data=$request->validate(['target_tier'=>['required','in:small,mid,premium'],'amount'=>['required','numeric','min:1'],'proof_details'=>['required','string','max:2000']]);OfflineUpgradeRequest::create($data+['school_id'=>Tenant::id(),'requested_by'=>$request->user()->id]);return back()->with('success','Upgrade request sent to the platform owner.');}
 public function paystack(Request $request):Response{abort_unless(hash_equals(hash_hmac('sha512',$request->getContent(),config('services.paystack.secret')),$request->header('x-paystack-signature','')),401);return $this->acceptWebhook('paystack',$request->all());}
 public function flutterwave(Request $request):Response{abort_unless(hash_equals(config('services.flutterwave.webhook_hash'),$request->header('verif-hash','')),401);return $this->acceptWebhook('flutterwave',$request->all());}
 private function acceptWebhook(string $provider,array $payload):Response{/* Payment activation service is intentionally idempotent and added in phase 2. */return response('ok');}
}
