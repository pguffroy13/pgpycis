"""
Command-line interface for pgpycis
"""

import click
import sys
from .core import PGPYCIS
from .healthcheck import check_postgres_service, verify_postgres_connection


@click.command()
@click.option(
    "-U", "--user",
    default="postgres",
    help="PostgreSQL user [default: postgres]"
)
@click.option(
    "-h", "--host",
    default="localhost",
    help="PostgreSQL server host [default: localhost]"
)
@click.option(
    "-p", "--port",
    type=int,
    default=5432,
    help="PostgreSQL server port [default: 5432]"
)
@click.option(
    "-d", "--database",
    default="postgres",
    help="PostgreSQL database [default: postgres]"
)
@click.option(
    "-D", "--pgdata",
    envvar="PGDATA",
    help="PostgreSQL data directory [$PGDATA]"
)
@click.option(
    "-f", "--format",
    type=click.Choice(["text", "html"]),
    default="text",
    help="Output format [default: text]"
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file (stdout if not specified)"
)
@click.option(
    "-l", "--language",
    type=click.Choice(["en_US", "fr_FR", "zh_CN"]),
    default="en_US",
    help="Report language [default: en_US]"
)
@click.option(
    "--version",
    is_flag=True,
    help="Show version"
)
def main(user, host, port, database, pgdata, format, output, language, version):
    """PGPYCIS - PostgreSQL CIS Compliance Assessment Tool
    
    A comprehensive security assessment tool that checks PostgreSQL
    clusters against the CIS PostgreSQL Benchmark and additional security
    controls.
    """
    
    if version:
        from . import __version__
        click.echo(f"pgpycis v{__version__}")
        return
    
    # Pre-flight checks: verify PostgreSQL service is running
    click.echo("Running pre-flight checks...", err=True)
    
    # Check 1: Verify PostgreSQL service is active
    is_running, service_msg = check_postgres_service(host=host, port=port)
    if not is_running:
        click.secho(f"✗ {service_msg}", fg="red", err=True)
        sys.exit(1)
    else:
        click.secho(f"✓ {service_msg}", fg="green", err=True)
    
    # Check 2: Verify database connection
    can_connect, conn_msg = verify_postgres_connection(user=user, host=host, 
                                                       port=port, database=database)
    if not can_connect:
        click.secho(f"✗ {conn_msg}", fg="red", err=True)
        sys.exit(1)
    else:
        click.secho(f"✓ {conn_msg}", fg="green", err=True)
    
    click.echo("Pre-flight checks passed. Starting assessment...\n", err=True)
    
    try:
        # Initialize assessment tool
        assessment = PGPYCIS(
            user=user,
            host=host,
            port=port,
            database=database,
            pgdata=pgdata,
            lang=language
        )
        
        # Run assessment
        if not assessment.run(format=format, output_file=output):
            sys.exit(1)
    
    except KeyboardInterrupt:
        click.secho("\nAssessment interrupted by user", fg="yellow")
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
