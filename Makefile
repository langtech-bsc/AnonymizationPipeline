deploy:
	docker compose -f docker-compose-demo.yml up --build -d
undeploy:
	docker compose -f docker-compose-demo.yml down
stop:
	docker compose -f docker-compose-demo.yml stop