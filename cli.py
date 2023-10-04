import os
import click
from pyngrok import ngrok
from gpu_box.server import run_server


@click.group()
def main():
    """Main command group."""



@main.command()
@click.option("--token", default=os.environ.get("NGROK_TOKEN"), help="Ngrok token.")
@click.option(
    "--domain",
    default=os.environ.get("NGROK_DOMAIN"),
    help="Domain to be used.",
)
@click.option(
    "--oauth-provider",
    default=os.environ.get("NGROK_OAUTH_PROVIDER", "google"),
    help="OAuth provider.",
)
@click.option(
    "--allowed-emails",
    multiple=True,
    default=(os.environ.get("NGROK_ALLOWED_EMAILS", "").split(",")),
    help="Allowed emails for OAuth.",
)
def oauth(token, domain, oauth_provider, allowed_emails):
    """Set up ngrok tunneling using OAuth."""
    ngrok.set_auth_token(token)
    config = {
        "oauth": {"provider": oauth_provider, "allow_emails": list(allowed_emails)},
        "domain": domain,
    }
    ngrok_tunnel = ngrok.connect(8000, **config)
    print("Public URL:", ngrok_tunnel.public_url)
    run_server()


@main.command()
@click.option("--token", default=os.environ.get("NGROK_TOKEN"), help="Ngrok token.")
@click.option(
    "--domain",
    default=os.environ.get("NGROK_DOMAIN"),
    help="Domain to be used.",
)
@click.option(
    "--auth-pairs",
    multiple=True,
    default=os.environ.get("NGROK_AUTH_PAIRS", "").split(","),
    help="Username and password pairs in the format username:password. Can specify multiple.",
)
def password(token, domain, auth_pairs):
    """Set up ngrok tunneling using basic authentication."""
    if not auth_pairs:
        raise click.ClickException(
            "At least one auth pair must be specified in the format username:password."
        )

    ngrok.set_auth_token(token)

    # Extracting the username:password pairs
    basic_auth_list = [pair for pair in auth_pairs if ":" in pair]
    if len(basic_auth_list) != len(auth_pairs):
        raise click.ClickException(
            "All auth pairs must be in the format username:password."
        )

    config = {"domain": domain, "basic_auth": basic_auth_list}

    ngrok_tunnel = ngrok.connect(8000, **config)
    print("Public URL:", ngrok_tunnel.public_url)
    run_server()


@main.command()
def serve():
    run_server()



if __name__ == "__main__":
    main()
