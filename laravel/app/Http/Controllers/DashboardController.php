<?php
namespace App\Http\Controllers;use App\Models\Result;use App\Models\Student;use App\Services\Tenant;use Illuminate\View\View;
class DashboardController {public function __invoke():View{$school=Tenant::current();return view('dashboard',compact('school')+['students'=>Student::whereBelongsTo($school)->count(),'results'=>Result::whereBelongsTo($school)->count()]);}}
