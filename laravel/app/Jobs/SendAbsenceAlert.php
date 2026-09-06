<?php
namespace App\Jobs;
use App\Models\NotificationLog;use App\Models\Student;use Illuminate\Contracts\Queue\ShouldQueue;use Illuminate\Foundation\Queue\Queueable;
class SendAbsenceAlert implements ShouldQueue {use Queueable;public function __construct(public int $studentId,public string $date){}public function handle():void{$student=Student::with('guardians')->findOrFail($this->studentId);foreach($student->guardians as $guardian)NotificationLog::create(['school_id'=>$student->school_id,'student_id'=>$student->id,'channel'=>'sms','recipient'=>$guardian->phone,'template'=>'student_absent','message'=>"Dear Parent, your child {$student->full_name} was marked absent from school today ({$this->date}). Please contact the school if necessary.",'status'=>'queued']);}}
