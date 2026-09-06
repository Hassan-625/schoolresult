<?php
use Illuminate\Support\Facades\Schedule;
Schedule::command('schoolcloud:compile-results')->dailyAt('01:00')->withoutOverlapping()->onOneServer();
