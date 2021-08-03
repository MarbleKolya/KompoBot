DELETE FROM total_result 
INSERT INTO total_result 
select u.id as user_id,user_name, user_secondName,
result_test1.score as result_test1,
result_test2.score as result_test2,
result_test3.score as result_test3,
result_test4.score as result_test4,
result_test5.score as result_test5,
result_test6.score as result_test6,
result_test7.score as result_test7,
result_test8.score as result_test8,
result_test9.score as result_test9,
result_test10.score as result_test10,
result_test11.score as result_test11,
result_test12.score as result_test12,
result_test13.score as result_test13,
result_test14.score as result_test14,
result_test15.score as result_test15,
result_test16.score as result_test16,
result_test17.score as result_test17,
total_resultOffice.Total_Score as Total_ScoreOffice,
total_resultMP.Total_Score as Total_ScoreMP,
(total_resultOffice.Total_Score * 100 / 40)||'%' as ProgressOffice,
(total_resultMP.Total_Score * 100 / 130)||'%' as ProgressMP,
total_resultOffice.test_completed as TestCompletedOffice,
total_resultMP.test_completed as TestCompletedMP,
iif(total_resultOffice.test_completed=4, 1,0) as CompletedOfiiceCourse,
iif(total_resultMP.test_completed=13, 1,0) as CompletedMPCourse,
iif(total_resultOffice.Total_Score=40, 'Yes','NO') as CompletedOfiiceCourseSuccessfull,
iif(total_resultMP.Total_Score=130, 'Yes','NO') as CompletedMPCourseSuccessfull
from users u
left JOIN users_result result_test1
on u.id=result_test1.user_id
and result_test1.test_number = 1
left JOIN users_result result_test2
on u.id=result_test2.user_id
and result_test2.test_number = 2
left JOIN users_result result_test3
on u.id=result_test3.user_id
and result_test3.test_number = 3
left JOIN users_result result_test4
on u.id=result_test4.user_id
and result_test4.test_number = 4
left JOIN users_result result_test5
on u.id=result_test5.user_id
and result_test5.test_number = 5
left JOIN users_result result_test6
on u.id=result_test6.user_id
and result_test6.test_number = 6
left JOIN users_result result_test7
on u.id=result_test7.user_id
and result_test7.test_number = 7
left JOIN users_result result_test8
on u.id=result_test8.user_id
and result_test8.test_number = 8
left JOIN users_result result_test9
on u.id=result_test9.user_id
and result_test9.test_number = 9
left JOIN users_result result_test10
on u.id=result_test10.user_id
and result_test10.test_number = 10
left JOIN users_result result_test11
on u.id=result_test11.user_id
and result_test11.test_number = 11
left JOIN users_result result_test12
on u.id=result_test12.user_id
and result_test12.test_number = 12
left JOIN users_result result_test13
on u.id=result_test13.user_id
and result_test13.test_number = 13
left JOIN users_result result_test14
on u.id=result_test14.user_id
and result_test14.test_number = 14
left JOIN users_result result_test15
on u.id=result_test15.user_id
and result_test15.test_number = 15
left JOIN users_result result_test16
on u.id=result_test16.user_id
and result_test16.test_number = 16
left JOIN users_result result_test17
on u.id=result_test17.user_id
and result_test17.test_number = 17
left JOIN (
Select user_id, sum(score) as Total_Score,
sum(case when ifnull(score,0) > 0 then 1 else 0 END) as test_completed  from users_result
WHERE test_number<=4
GROUP by user_id
) total_resultOffice
on u.id=total_resultOffice.user_id
left JOIN (
Select user_id, sum(score) as Total_Score,
sum(case when ifnull(score,0) > 0 then 1 else 0 END) as test_completed  from users_result
WHERE test_number>4 AND test_number<=17
GROUP by user_id
) total_resultMP
on u.id=total_resultMP.user_id
