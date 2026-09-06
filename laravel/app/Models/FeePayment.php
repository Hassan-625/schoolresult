<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class FeePayment extends Model {protected $guarded=[];protected $casts=['paid_at'=>'datetime'];public function invoice(){return $this->belongsTo(FeeInvoice::class,'fee_invoice_id');}protected static function booted():void{static::updating(fn()=>throw new \LogicException('Issued receipts are immutable. Record an audited reversal.'));static::deleting(fn()=>throw new \LogicException('Issued receipts cannot be deleted.'));}}
