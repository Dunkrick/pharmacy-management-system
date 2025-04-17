import click
from flask.cli import with_appcontext
from extensions import db
from models import User

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(username, email, password):
    """Create an admin user."""
    try:
        user = User(
            username=username,
            email=email,
            is_admin=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin user {username} created successfully!')
    except Exception as e:
        click.echo(f'Error creating admin user: {str(e)}') 