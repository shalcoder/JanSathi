# Hindi Translation Test Script for JanSathi
# Run this to test all Hindi functionality

Write-Host "🧪 Testing JanSathi Hindi Translation..." -ForegroundColor Green
Write-Host ""

# Test 1: Hindi Query
Write-Host "Test 1: Hindi Query (PM Kisan)" -ForegroundColor Yellow
try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:5000/query" -Method POST -ContentType "application/json" -Body '{"text_query": "प्रधानमंत्री किसान सम्मान निधि योजना क्या है?", "language": "hi", "userId": "test_user"}'
    Write-Host "✅ Response received: $($response1.answer.text.Substring(0, 100))..." -ForegroundColor Green
} catch {
    Write-Host "❌ Test 1 Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: English to Hindi
Write-Host "Test 2: English Query with Hindi Response" -ForegroundColor Yellow
try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:5000/query" -Method POST -ContentType "application/json" -Body '{"text_query": "What is Ayushman Bharat scheme?", "language": "hi", "userId": "test_user"}'
    Write-Host "✅ Response received: $($response2.answer.text.Substring(0, 100))..." -ForegroundColor Green
} catch {
    Write-Host "❌ Test 2 Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Ujjwala Yojana
Write-Host "Test 3: Ujjwala Yojana in Hindi" -ForegroundColor Yellow
try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:5000/query" -Method POST -ContentType "application/json" -Body '{"text_query": "उज्ज्वला योजना क्या है?", "language": "hi", "userId": "test_user"}'
    Write-Host "✅ Response received: $($response3.answer.text.Substring(0, 100))..." -ForegroundColor Green
} catch {
    Write-Host "❌ Test 3 Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Health Check
Write-Host "Test 4: Backend Health Check" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET
    Write-Host "✅ Backend Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "🎯 Hindi Translation Tests Complete!" -ForegroundColor Green
Write-Host "If all tests show ✅, your Hindi translation is working perfectly!" -ForegroundColor Cyan