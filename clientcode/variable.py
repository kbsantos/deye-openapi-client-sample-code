
# data center EU's url https://eu1-developer.deyecloud.com/v1.0
# or US's url https://us1-developer.deyecloud.com/v1.0

baseurl = "https://eu1-developer.deyecloud.com/v1.0"
token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsib2F1dGgyLXJlc291cmNlIl0sInVzZXJfbmFtZSI6IjBfa3Jzc2FudG9zMThAZ21haWwuY29tXzIiLCJzY29wZSI6WyJhbGwiXSwiZGV0YWlsIjp7Im9yZ2FuaXphdGlvbklkIjowLCJ0b3BHcm91cElkIjpudWxsLCJncm91cElkIjpudWxsLCJyb2xlSWQiOi0xLCJ1c2VySWQiOjEzMDI1ODY1LCJ2ZXJzaW9uIjoxMDAwLCJpZGVudGlmaWVyIjoia3Jzc2FudG9zMThAZ21haWwuY29tIiwiaWRlbnRpdHlUeXBlIjoyLCJtZGMiOiJldSIsImFwcElkIjoiMjAyNDA5MTc1NTM3MDA2IiwibWZhU3RhdHVzIjpudWxsLCJ0ZW5hbnQiOiJEZXllIn0sImV4cCI6MTc3NDIwMjA5NCwibWRjIjoiZXUiLCJhdXRob3JpdGllcyI6WyJhbGwiXSwianRpIjoiZTg0YTQ0MzAtY2QyNS00MDAyLWI5M2EtYmEwMjE1OTc5ODQyIiwiY2xpZW50X2lkIjoidGVzdCJ9.bB7d4slCbctzfXRTgFZo8656kOmCkvl-_C-kr6iZFPo5pE578R4mcPcc0N_RqUNxKIR-gJ_UNxzpAz7Im9cVvXyvtlBfAFNTMt78ktEPJLoHAc_Hr9LI1ZNW10tPcV6WWGVnIyMJxN5fAteb8tRfjU8Fd0T2BzlVie0PY9ayiQb-YYWxK60id0qI9_bvIaeyvEJ-SEhi_9Bp6cs-WboJ01m3Zt182fhdCTZsGGAQjL7vbIrsdCGGKlBwrg389H1V4evJzRNChZ63eqDb1YmRSxHDhFFwz5EVXciMnQtkzbnjI4CfuDj-clJIbarY9WBWmYtGw1piFJiAqnqWhiBGVw'  # Replace the token, and you cloud get it by obtain_token.py
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'bearer ' + token
}


# Token Configuration Variables
app_id = "202409175537006"  # Replace with your appId
app_secret = "31542b5feffc46e9f21c4b09851f3f0f"  # Replace with your appSecret
email = "krssantos18@gmail.com"  # Replace with your email
company_id = "0"  # Replace with your companyId
password = "Kbcs1824"  # Replace with your password for www.deyecloud.com

