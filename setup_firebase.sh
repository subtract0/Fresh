#!/bin/bash
# Firebase Environment Setup for Fresh AI
# This script sets up Firebase credentials for persistent memory

# Set environment variables for Firebase
export FIREBASE_PROJECT_ID="gothic-point-390410"
export FIREBASE_CLIENT_EMAIL="firebase-adminsdk-fbsvc@gothic-point-390410.iam.gserviceaccount.com"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCvt9a+0DtFk5lb
VkZ7VmAGkfbodL3dQ2zHakbZ34Om3VYvV7BbeAtNn62gCXx/BHHhEOyXD0lUR1Jv
3RoJwtY4L0M125Nfli4fPoWvn/Elg6KKMIEp6ILqQvFQZNzTMdriekldzKDFknO9
+WAo5GVz+Fkz617+MvCJcEpI4/xDyHazs4ZSlPN5dgKkVLgmSB8U5wWAhQycGWSH
EWSk+6FDYKvz2To8cCH/23Bmona9EI1Gi3AkbpjHGJuZ0NZKuA/ACqEyL0ArXuxF
VkRylLQx4AZ97q5+7sTvS7XrktKNUPtfCQouCk9zEvhNjvKcusqmyP+w8JFgloZY
bN2bAjHdAgMBAAECggEADB9GyXd3Ef01OrJbKWi+NiXSs/BTJX+1x5S4L5FLtUgW
s9cSUQpuiTEyBVTc3wGw/ixbOK6ddJrOVUOaZ2r8DqM1Y/KdGkkzhFnyrLjVe4I3
GokZwrOKIzFxZrDr9QaUSZnTFDf+LV3FmKkAA8IskjwN91bOVliwSbhSlPBkIk7a
l+gnyJt1Wc1zC8P9H6PoSAFMaPtdH/Mc9qGUg8mMjqnsibaMh/6+fNgrzcbkHbzn
6sXSQ+n5VjyAXjmxArPPMxH2Zoai0xocLKDWSvkZCflCxkH61FMRTaPytkwqtJ8N
3YlBPRlsBANhmtV3+Pjb7AF7yFPfM/FMHoJlKw3LBwKBgQD3o+oKPWvY46D6I2cU
lqaqHeBL1STs7q5jLaJeE7BzE5SWoGVm7MkiHAmS9Y4VIjNlYWE/wkt+JvWya4yG
EUcDJLiGjGSqmSwkPqJp117ENE+4g8WczcgIeeadEuG04D3Jq12JVc5EhPxxypxg
z6H31700C2WlqhpnVCpBFuyTLwKBgQC1pmEoAviUqH29P+BeAJwcSh/yLBw3wxJz
2F6bNZIqY/AtnmWb2MuipXz9JNOJHsPO+AGxOV1h+hcn4JsLt5QaqlXcmXIQOI8i
zpRbfW70qGVVOUyOnMhPkjEuugJg6JIRMgQv3SH6+b+me0yhFUpzH9LRHxVq9Edm
7cVS7as4swKBgCe2o7vMqdT4fEJhFxDYMBYsAGJo5ikRBepl0RohMjTiOPwG8PwW
kRLlSCvHMWf2OiPSABSHhi/O86wPT1PYxXidlPIO5b3uHoQZf1ZV8Z6pfPdsOm6x
GZkyY2dhNc0aAQ6saq2xkwiuAwYEphtocOMcN/12rnBo3R8hAj25/WqFAoGASaiI
9x+VSzqzmh0fzx5yLyqDn8DxRE9O2TjgzBFCDvxtdSIo07Rqhq6Sa1gWiyC1h+Sb
UxEO4970qs/yLyMm5FUz8fsq/Jbiu9uG3z6S0pTCWnecqqu6skF2vhrhQgisylo8
xmfmEo5Zf5m57gvjH6HE69Wt6qvZlExQWptTde8CgYEApuyz4pNnFwEopeqfyOSG
yTIROB0WRsxlOP0uITY89cfiKWi6xJD8YNEHogSuxQZgMfDt+diuftRsjZhHwX1I
5ts9AaZ++SlIW/3Ai/6OlgSltD7QZunBuBRb+dxM6SFdekbynmyIDjxoHSnQQ/D7
bLg0NhGS2UozAZJUwnugl2k=
-----END PRIVATE KEY-----"

# Alternative: Set path to credentials file
export GOOGLE_APPLICATION_CREDENTIALS="/Users/am/Code/Fresh/.secrets/firebase-admin-sdk.json"

echo "✅ Firebase environment variables set!"
echo "🔑 Project ID: $FIREBASE_PROJECT_ID"
echo "📧 Client Email: $FIREBASE_CLIENT_EMAIL"
echo "🔐 Private Key: Set"
echo "📄 Credentials File: $GOOGLE_APPLICATION_CREDENTIALS"
echo ""
echo "Now you can run Fresh CLI with persistent memory:"
echo "  poetry run python -m ai.cli.fresh --use-firestore spawn 'your task'"
