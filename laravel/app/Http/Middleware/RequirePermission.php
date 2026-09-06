<?php
namespace App\Http\Middleware;
use Closure;use Illuminate\Http\Request;use Symfony\Component\HttpFoundation\Response;
class RequirePermission {
 private const MAP=['proprietor'=>['students.read','students.write','academics.read','academics.write','results.approve','results.lock','attendance','finance.read','finance.write','staff.manage','subscription.manage'],'headmaster'=>['students.read','students.write','academics.read','academics.write','results.approve','results.lock','attendance','staff.assign'],'accountant'=>['students.read','finance.read','finance.write'],'teacher'=>['students.read','academics.read','academics.write','attendance']];
 public function handle(Request $request,Closure $next,string $permission,?string $feature=null):Response{$user=$request->user();if($user?->is_super_admin)return $next($request);$pivot=$request->attributes->get('membership');abort_unless($pivot&&in_array($permission,self::MAP[$pivot->role]??[],true),403);$school=$request->attributes->get('school');abort_unless($school->active(),402,'Subscription inactive.');if($feature)abort_unless($school->allows($feature),403,'Feature unavailable on this tier.');return $next($request);}
}
