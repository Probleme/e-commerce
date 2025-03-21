all: up

get_ip:
	chmod +x get_ip.sh
	./get_ip.sh

up: get_ip build
	docker-compose -f docker-compose.yml up #-d

build:
	docker-compose -f docker-compose.yml build

start:
	docker-compose -f docker-compose.yml start

stop:
	docker-compose -f docker-compose.yml stop

down:
	docker-compose -f docker-compose.yml down

clean: down

fclean: clean
	docker system prune -a --volumes -f

re: fclean all

.PHONY: all build down clean fclean re get_ip