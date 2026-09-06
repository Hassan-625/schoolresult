<?php
namespace App\Services;
final class ResultCommentGenerator {
 public function generate(float $average,int $absences=0):array{$teacher=match(true){$average>=85=>'An outstanding performance. Keep sustaining this excellent standard.',$average>=75=>'A very good performance with strong understanding across subjects.',$average>=65=>'A good performance. Greater consistency will produce excellent results.',$average>=55=>'A fair performance with clear room for improvement.',$average>=40=>'More guided study and regular practice are strongly recommended.',default=>'Immediate academic support and close home-school follow-up are required.'};if($absences>=5)$teacher.=' Improved attendance is also essential.';$head=match(true){$average>=75=>'Excellent progress.',$average>=55=>'Promising progress; keep working hard.',$average>=40=>'Fair effort; greater commitment is expected.',default=>'Performance requires urgent improvement.'};return compact('teacher','head');}
}
