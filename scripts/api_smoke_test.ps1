param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$UserId = "smoke_user"
)

$ErrorActionPreference = "Stop"

$health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/health"
if ($health.status -ne "ok") {
    throw "Health check failed"
}

$sessionBody = @{
    user_id = $UserId
    training_mode = "LOW"
    noise_profile = "none"
} | ConvertTo-Json
$session = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/sessions" `
    -ContentType "application/json" `
    -Body $sessionBody

$task = Invoke-RestMethod `
    -Method Get `
    -Uri "$BaseUrl/api/v1/tasks/next?session_id=$($session.session_id)"

$answerBody = @{
    session_id = $session.session_id
    task_id = $task.task_id
    user_input = $task.target_text
} | ConvertTo-Json
$answer = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/answers" `
    -ContentType "application/json" `
    -Body $answerBody

$progress = Invoke-RestMethod `
    -Method Get `
    -Uri "$BaseUrl/api/v1/users/$UserId/progress"

[PSCustomObject]@{
    health = $health.status
    session_id = $session.session_id
    task_id = $task.task_id
    answer_correct = $answer.correct
    total_answers = $progress.total_answers
    accuracy = $progress.accuracy
}
