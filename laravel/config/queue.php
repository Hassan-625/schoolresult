<?php
return ['default'=>env('QUEUE_CONNECTION','redis'),'connections'=>['database'=>['driver'=>'database','table'=>'jobs','queue'=>'default','retry_after'=>90],'redis'=>['driver'=>'redis','connection'=>'default','queue'=>'default','retry_after'=>90]],'failed'=>['driver'=>'database-uuids','database'=>env('DB_CONNECTION','pgsql'),'table'=>'failed_jobs']];
