<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;use Illuminate\Database\Eloquent\Relations\BelongsTo;use Illuminate\Database\Eloquent\Relations\HasMany;
class Student extends Model {
 protected $fillable=['school_id','user_id','first_name','last_name','reg_no','class_level','department','level','term','session','term_ending','next_term_begins'];
 protected $casts=['term_ending'=>'date','next_term_begins'=>'date'];
 public function school():BelongsTo{return $this->belongsTo(School::class);} public function results():HasMany{return $this->hasMany(Result::class);}
 public function getFullNameAttribute():string{return trim("{$this->first_name} {$this->last_name}");}
 protected static function booted():void{static::creating(function(Student $student){$limit=$student->school->studentLimit();if($limit!==null&&$student->school->students()->count()>=$limit)abort(422,"Student limit reached. Upgrade the school's tier.");});}
}
