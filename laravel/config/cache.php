<?php
return ['default'=>env('CACHE_STORE','database'),'stores'=>['database'=>['driver'=>'database','connection'=>null,'table'=>'cache'],'redis'=>['driver'=>'redis','connection'=>'default']],'prefix'=>'schoolcloud_'];
