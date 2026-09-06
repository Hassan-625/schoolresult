<?php
namespace App\Models;use Illuminate\Database\Eloquent\Model;
class OfflineUpgradeRequest extends Model {protected $guarded=[];protected $casts=['reviewed_at'=>'datetime'];public function school(){return $this->belongsTo(School::class);}}
