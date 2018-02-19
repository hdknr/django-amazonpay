from django.utils import translation, timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import djclick as click
from datetime import timedelta
from amzpay import models, encoders
from logging import getLogger
log = getLogger()

translation.activate('ja')


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    pass


def find_auth(id):
    if id.isdigit():
        return models.PayAuth.objects.filter(id=id).first()
    else:
        return models.PayAuth.objects.filter(authorization_id=id).first()


@main.command()
@click.argument('auth_id')
@click.option('--reason', '-r', default='close')
@click.option('--client', '-c', default=None)
@click.pass_context
def close(ctx, auth_id, reason, client):
    ''' Close Auth '''

    client = client and models.Client.objects.filter(id=client).first()
    if client:
        # force close
        response = client.api.close_authorization(
            amazon_authorization_id=auth_id,
            closure_reason=reason)
        click.echo("Force Closing {}".format(auth_id))
        click.echo(encoders.to_json(response.to_dict(), indent=2))
        return

    auth = find_auth(auth_id)
    if auth:
        click.echo("Closing {}".format(auth.authorization_id))
        click.echo(auth.close(reason=reason).response)


@main.command()
@click.argument('id')
@click.pass_context
def capture(ctx, id):
    ''' Capture Auth '''

    auth = find_auth(id)
    capture = auth and auth.create_capture()
    if capture:
        click.echo("Capture {}".format(auth.authorization_id))
        click.echo(capture.capture().response)


@main.command()
@click.argument('auth_id')
@click.pass_context
def update_detail(ctx, auth_id):
    ''' Update Auth Detail'''

    auth = find_auth(auth_id)
    if auth:
        click.echo("Update {}".format(auth.authorization_id))
        click.echo(auth.get_detail().response)
    else:
        click.echo("Auth Not Found :{}".format(auth_id))


@main.command()
@click.argument('call_id')
@click.pass_context
def call(ctx, call_id):
    ''' Auth Call Detail'''
    call = models.PayAuthCall.objects.filter(id=call_id).first()
    click.echo(encoders.to_json(
        {'action': call.action, 'success': call.success,
         'request': call.request_object,
         'response': call.response_object,}))


@main.command()
@click.argument('auth_id')
@click.pass_context
def describe(ctx, auth_id):
    ''' Auth Detail'''
    auth = find_auth(auth_id)
    click.echo(auth.latest.response)
