<?php
namespace App\Models;use Illuminate\Database\Eloquent\Model;
class SubscriptionPayment extends Model {protected $guarded=[];protected $casts=['paid_at'=>'datetime','metadata'=>'array'];public function school(){return $this->belongsTo(School::class);}}
