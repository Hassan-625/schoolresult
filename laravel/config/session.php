<?php
return ['driver'=>env('SESSION_DRIVER','database'),'lifetime'=>120,'encrypt'=>true,'files'=>storage_path('framework/sessions'),'connection'=>null,'table'=>'sessions','cookie'=>env('SESSION_COOKIE','schoolcloud_session'),'path'=>'/','domain'=>env('SESSION_DOMAIN'),'secure'=>env('SESSION_SECURE_COOKIE',true),'http_only'=>true,'same_site'=>'lax'];
