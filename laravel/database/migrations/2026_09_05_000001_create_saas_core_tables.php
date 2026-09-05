<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
return new class extends Migration {
 public function up(): void {
  Schema::create('schools',function(Blueprint $t){$t->id();$t->string('name');$t->string('slug')->unique();$t->string('email')->nullable();$t->string('phone')->nullable();$t->enum('tier',['small','mid','premium'])->default('small');$t->enum('subscription_status',['trial','active','suspended','expired'])->default('trial');$t->timestamp('subscription_expires_at')->nullable();$t->timestamps();});
  Schema::table('users',function(Blueprint $t){$t->boolean('is_super_admin')->default(false)->index();});
  Schema::create('school_user',function(Blueprint $t){$t->id();$t->foreignId('school_id')->constrained()->cascadeOnDelete();$t->foreignId('user_id')->constrained()->cascadeOnDelete();$t->enum('role',['proprietor','headmaster','accountant','teacher']);$t->json('custom_permissions')->nullable();$t->boolean('is_active')->default(true);$t->timestamps();$t->unique(['school_id','user_id']);});
  Schema::create('class_assignments',function(Blueprint $t){$t->id();$t->foreignId('school_id')->constrained()->cascadeOnDelete();$t->foreignId('user_id')->constrained()->cascadeOnDelete();$t->string('class_level');$t->boolean('can_enter_results')->default(true);$t->boolean('can_take_attendance')->default(true);$t->timestamps();$t->unique(['school_id','user_id','class_level']);});
 }
 public function down(): void {Schema::dropIfExists('class_assignments');Schema::dropIfExists('school_user');Schema::table('users',fn(Blueprint $t)=>$t->dropColumn('is_super_admin'));Schema::dropIfExists('schools');}
};
