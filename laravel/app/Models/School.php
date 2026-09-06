<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;use Illuminate\Database\Eloquent\Relations\BelongsToMany;use Illuminate\Database\Eloquent\Relations\HasMany;
class School extends Model {
 protected $fillable=['name','slug','email','phone','tier','subscription_status','subscription_expires_at']; protected $casts=['subscription_expires_at'=>'datetime'];
 public function users():BelongsToMany{return $this->belongsToMany(User::class)->withPivot(['role','custom_permissions','is_active'])->withTimestamps();}
 public function students():HasMany{return $this->hasMany(Student::class);}
 public function active():bool{return in_array($this->subscription_status,['active','trial'],true)&&(!$this->subscription_expires_at||$this->subscription_expires_at->isFuture());}
 public function allows(string $feature):bool{return in_array($feature,config("tiers.{$this->tier}.features",[]),true);}
 public function studentLimit():?int{return config("tiers.{$this->tier}.student_limit");}
}
