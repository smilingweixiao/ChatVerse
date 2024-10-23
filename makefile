PORT1 = 3000
PORT2 = 5000

frontend:
	cd client && npm install && npm run dev

backend:
	cd server && python app.py

agent%:
	curl 127.0.0.1:$(PORT2)/api/console/$*

# Phony targets
.PHONY: all clean