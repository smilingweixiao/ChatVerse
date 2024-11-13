PORT1 = 3000
PORT2 = 5000

.PHONY: frontend backend backendLocal agent% clean

frontend:
	@echo ===============================================
	@echo Frontend is running on http://localhost:$(PORT1)
	@echo ===============================================
	@cd client && npm install && npm run dev

backendLocal:
	@cd server && python app.py

clean:
	docker rm -f chatverse

agent%:
	curl 127.0.0.1:$(PORT2)/api/console/$*
