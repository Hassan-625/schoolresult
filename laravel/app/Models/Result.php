<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;use Illuminate\Database\Eloquent\Relations\BelongsTo;
class Result extends Model {
 protected $fillable=['school_id','student_id','subject_id','first_ca','second_ca','exam','first_term','second_term'];
 public function student():BelongsTo{return $this->belongsTo(Student::class);} public function subject():BelongsTo{return $this->belongsTo(Subject::class);}
 protected static function booted():void{static::saving(function(Result $r){if($r->school_id!==$r->student->school_id||$r->school_id!==$r->subject->school_id)abort(422,'Tenant mismatch.');$r->total=$r->first_ca+$r->second_ca+$r->exam;$r->subject_average=round(($r->total+$r->first_term+$r->second_term)/3,2);$r->grade=match(true){$r->total>=75=>'A',$r->total>=65=>'B',$r->total>=55=>'C',$r->total>=45=>'D',$r->total>=40=>'E',default=>'F'};$r->remark=['A'=>'Excellent','B'=>'Good','C'=>'Average','D'=>'Fair','E'=>'Poor','F'=>'Fail'][$r->grade];});}
}
