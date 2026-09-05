<?php
namespace App\Http\Middleware;
use Closure;use Illuminate\Http\Request;use Symfony\Component\HttpFoundation\Response;
class ResolveSchool {public function handle(Request $request,Closure $next):Response{$user=$request->user();if($user&&!$user->is_super_admin){$school=$user->schools()->wherePivot('is_active',true)->first();abort_unless($school,403,'No active school membership.');app()->instance('tenant',$school);$request->attributes->set('school',$school);$request->attributes->set('membership',$school->pivot);}return $next($request);}}
