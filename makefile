PORT1 = 3000
PORT2 = 5000

.PHONY: frontend backend backendLocal agent% clean

frontend:
	@echo ===============================================
	@echo Frontend is running on http://localhost:$(PORT1)
	@echo ===============================================
	@cd client && npm install && npm run dev

backend:
	@docker run --rm -d -p $(PORT2):$(PORT2) --name chatverse mike911209/chatverse
	@echo ===============================================
	@echo Backend is running on http://localhost:$(PORT2)
	@echo ===============================================

backendLocal:
	@cd server && python app.py

clean:
	docker rm -f chatverse

agent%:
	curl 127.0.0.1:$(PORT2)/api/console/$*
