<?php
namespace App\Services;use App\Models\School;
final class Tenant {public static function current():School{return app('tenant');}public static function id():int{return self::current()->id;}}
