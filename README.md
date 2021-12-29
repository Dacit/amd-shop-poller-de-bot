# amd-shop-poller-de-bot

Bot that polls the German amd website and notifies users when items become available.

## Usage
Build docker image and run. Configuration variables: 
- `BOT_TOKEN`: telegram bot api token for your instance
- `BOT_DATA_DIR`: directory for persistent data (default `/bot`)

See the [docker-compose](docker-compose.yml) for an usage example.
To use the compose project, fill in your secret in the [.env](.env) file and run `docker-compose up -d`.
