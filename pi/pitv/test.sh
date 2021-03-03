
#BASE_URL="http://localhost:5069/api/v1.0/telegramBOT"
BASE_URL="http://192.168.1.63:5069/api/v1.0/pipapi"


echo "Test GET status..."
curl -i $BASE_URL/status


