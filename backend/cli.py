# -*- coding: utf-8 -*-
"""
CLI entry point for Entertwine Chatbot
"""

import logging
import click
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Entertwine Chatbot CLI"""
    pass


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=3978, help='Port to bind to')
@click.option('--workers', default=1, help='Number of worker processes')
def start(host, port, workers):
    """Start the Entertwine Chatbot server"""
    try:
        from .app import create_app
        logger.info(f"Starting Entertwine Chatbot on {host}:{port} with {workers} workers")
        
        import uvicorn
        app = create_app()
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers if workers > 1 else 1,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


@cli.command()
def validate_config():
    """Validate configuration"""
    try:
        from .config import ChatbotConfig
        ChatbotConfig.validate()
        click.secho("✓ Configuration is valid", fg='green')
        sys.exit(0)
    except Exception as e:
        click.secho(f"✗ Configuration error: {e}", fg='red')
        sys.exit(1)


@cli.command()
def version():
    """Show version"""
    click.echo("Entertwine Chatbot SDK v1.0.0")


if __name__ == '__main__':
    cli()
