<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class FeeInvoice extends Model {protected $guarded=[];protected $casts=['due_date'=>'date'];public function school(){return $this->belongsTo(School::class);}public function student(){return $this->belongsTo(Student::class);}public function payments(){return $this->hasMany(FeePayment::class);}public function getBalanceAttribute():float{return max(0,(float)$this->amount_due-(float)$this->payments()->sum('amount'));}}
